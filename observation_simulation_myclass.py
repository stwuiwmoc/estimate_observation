# %%
import matplotlib
import numpy as np
from scipy import constants as phys_consts


def mkhelp(instance):
    import inspect
    attr_list = list(instance.__dict__.keys())
    for attr in attr_list:
        if attr.startswith("_"):
            continue
        print(attr)
    for method in inspect.getmembers(instance, inspect.ismethod):
        if method[0].startswith("_"):
            continue
        print(method[0] + "()")


def get_latest_commit_datetime() -> list[str]:
    """現在のツリーで直近のコミット日時を文字列として取得する

    Returns
    -------
    list[str]
        ["Latest commit datetime", コミットした日付, コミットした時刻]
    """

    import subprocess

    git_command = ["git", "log", "-1", "--format='%cI'"]

    proc = subprocess.run(
        git_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)

    latest_commit_date_text = proc.stdout.decode("utf-8")

    # タイムゾーンを表す "+0900" を削除
    latest_commit_datetime_text_without_timezone = latest_commit_date_text[1:-8]

    # 日付のみを含む文字列
    latest_commit_date_text = latest_commit_datetime_text_without_timezone[:10]

    # 時刻のみを含む文字列
    latest_commit_time_text = latest_commit_datetime_text_without_timezone[11:]

    return "Latest commit datetime", latest_commit_date_text, latest_commit_time_text


def have_some_change_in_git_status() -> bool:
    """git的な意味でのファイルの変更の有無をboolianで取得する

    Returns
    -------
    bool
        ファイルの変更箇所ありならTrue, 無しならFalse
    """

    import subprocess

    git_command = ["git", "status", "--short"]

    proc = subprocess.run(
        git_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)

    proc_text = proc.stdout.decode("utf-8")

    if len(proc_text) == 0:
        # git status --short で出力される文字列が無い
        # つまり「ファイルの変更箇所なし」を意味する
        have_some_change = False

    else:
        # git status --short で出力された文字列がある
        # つまり「ファイルに何かしらの変更箇所あり」を意味する
        have_some_change = True

    return have_some_change


def plot_parameter_table(
        fig: matplotlib.figure.Figure,
        position: matplotlib.gridspec.GridSpec,
        parameter_table: list,
        fontsize: int) -> matplotlib.axes._subplots.Axes:
    """パラメータ表示用のtableをax内に作成

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figureオブジェクト
    position: matplotlib.gridspec.GridSpec
        fig内での配置
    parameter_table : list
        パラメータリスト。縦横の要素数がそれぞれ一致している必要がある。（正方行列のように縦横で同じ要素数になる必要はない）
    fontsize : int
        テーブル内の文字サイズ

    Returns
    -------
    matplotlib.axes._subplots.AxesSubplot
        Axesオブジェクト
    """

    ax = fig.add_subplot(position)

    table = ax.table(
        cellText=parameter_table,
        loc="center")

    # fontsizeの調整
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)

    # 軸ラベルの消去
    ax.axis("off")

    # 縦幅をaxオブジェクトの縦幅に合わせて調整
    for pos, cell in table.get_celld().items():
        cell.set_height(1 / len(parameter_table))

    return ax


def calc_Plank_law_I_prime(rambda, T):
    """プランクの法則から波長と温度の関数として分光放射輝度を計算

    観測見積もり.md
        └ 望遠鏡の発光 \n
            └ プランクの法則 \n

    Parameters
    ----------
    rambda : float
        [m] 波長
    T : float
        [K] 黒体の温度

    Returns
    -------
    float
        [W / m^3 / sr] 黒体放射による分光放射輝度
    """

    h = phys_consts.h
    c = phys_consts.c
    k_B = phys_consts.k

    I_prime = (2 * h * c**2 / rambda**5) * (1 / (np.exp(h * c / (rambda * k_B * T)) - 1))

    return I_prime


class EmissionLineParameters:

    def __init__(
            self,
            rambda: float,
            N_H3p: float,
            g_ns: int,
            J_prime: int,
            A_if: float,
            E_prime: float,
            T_hypo: float) -> None:

        """各輝線のパラメータから発光輝線強度 I_obj を導出

        観測見積もり.md
            └ 観測対象の発光 \n
                └ H3+輝線の放射輝度 \n

        Parameters
        ----------
        rambda : float
            [m] 輝線の中心波長
        N_H3p : float
            _description_
        g_ns : int
            [無次元] nuclear spin weight, 2 or 4
        J_prime : int
            [無次元] 回転準位
        A_if : float
            [/s] アインシュタインのA係数
        E_prime : float
            [/cm] energy of upper statement
        T_hypo : float
            [K] 想定するH3+温度
        """

        # 入力されたパラメータの代入
        self.rambda = rambda
        self.N_H3p = N_H3p
        self.g_ns = g_ns
        self.J_prime = J_prime
        self.A_if = A_if
        self.E_prime = E_prime
        self.T_hypo = T_hypo

        # その他のパラメータの計算
        self.omega_if = 1 / self.rambda * 1e-2  # 波数 [/cm]
        self.Q_T = self.__calc_Q_T()

        # 発光輝線強度 I_obj の計算
        self.I_obj = self.__calc_I_obj()

    def h(self):
        mkhelp(self)

    def __calc_Q_T(self) -> float:
        """Partition function Q(T) の導出

        Returns
        -------
        float
            partition function Q(T)
        """
        T = self.T_hypo

        A_0 = - 1.11391
        A_1 = + 0.0581076
        A_2 = + 0.000302967
        A_3 = - 2.83724e-7
        A_4 = + 2.31119e-10
        A_5 = - 7.15895e-14
        A_6 = + 1.00150e-17

        Q_T = A_0 * T**0 + A_1 * T**1 + A_2 * T**2 + A_3 * T**3 + A_4 * T**4 + A_5 * T**5 + A_6 * T**6
        return Q_T

    def __calc_I_obj(self) -> float:

        N_H3p = self.N_H3p
        g_ns = self.g_ns
        J_prime = self.J_prime
        h = phys_consts.h
        c = phys_consts.c
        omega_if = self.omega_if
        A_if = self.A_if
        E_prime = self.E_prime
        k_b = phys_consts.k
        T_hypo = self.T_hypo
        Q_T = self.Q_T

        I_obj = N_H3p * g_ns * (2 * J_prime + 1) * h * c * (omega_if * 1e2) * A_if \
            * np.exp(- h * c * (E_prime * 1e2) / (k_b * T_hypo)) \
            / (4 * np.pi * Q_T)

        return I_obj


class TelescopeParameters:

    def __init__(
            self,
            T_GBT: float,
            D_t: float,
            FNO_t: float,
            tau_GBT: float,
            T_sky: float,
            tau_sky: float) -> None:

        """望遠鏡のパラメータを保持

        観測見積もり.md
            ├ 望遠鏡の発光 \n
            │   └ 望遠鏡の熱輻射による放射輝度 \n
            └ 地球大気の発光 \n
                └ 大気の熱輻射による放射輝度 \n

        Parameters
        ----------
        T_GBT : float
            [K] 望遠鏡光学系の温度
        D_t : float
            [m] 望遠鏡主鏡の口径
        FNO_t : float
            [無次元] 望遠鏡光学系の合成F値
        tau_GBT : float
            [無次元] 望遠鏡光学系の透過率
        T_sky : float
            [K] 大気温度
        tau_sky : float
            [無次元] 大気透過率
        """

        self.T_GBT = T_GBT
        self.D_t = D_t
        self.FNO_t = FNO_t
        self.tau_GBT = tau_GBT
        self.tau_sky = tau_sky
        self.T_sky = T_sky

        self.f_t = self.D_t * self.FNO_t
        self.A_t = np.pi * (self.D_t / 2) ** 2

    def h(self):
        mkhelp(self)

    def calc_I_GBT(self, rambda_: float, FWHM_fl: float) -> float:
        """観測波長に対するI_GBTを計算

        Parameters
        ----------
        rambda_ : float
            [m] 観測波長
        FWHM_fl : float
            [m] フィルターの半値幅

        Returns
        -------
        float
            [W / m^2 / sr]	1秒あたりの望遠鏡（鏡面など）からの熱輻射
        """
        T_GBT = self.T_GBT
        tau_GBT = self.tau_GBT

        I_prime = calc_Plank_law_I_prime(rambda=rambda_, T=T_GBT)
        I_GBT = I_prime * FWHM_fl * (1 - tau_GBT)

        return I_GBT

    def calc_I_sky(self, rambda_: float, FWHM_fl: float) -> float:
        """観測波長に対するI_skyを計算

        Parameters
        ----------
        rambda_ : float
            [m] 観測波長
        FWHM_fl : float
            [m] フィルターの半値幅

        Returns
        -------
        float
            [W / m^2 / sr]	1秒あたりの大気から熱輻射
        """
        T_sky = self.T_sky
        tau_sky = self.tau_sky

        I_prime = calc_Plank_law_I_prime(rambda=rambda_, T=T_sky)
        I_sky = I_prime * FWHM_fl * (1 - tau_sky)

        return I_sky


class InstrumentParameters:

    def __init__(
            self,
            telescope_params: TelescopeParameters,
            is_ESPRIT: bool,
            N_read: float,
            I_dark: float,
            G_Amp: float,
            has_fiber: bool,
            l_fb: float,
            rambda_fl_center: float,
            tau_fl_center: float,
            FWHM_fl: float) -> None:
        """イメージャー、分光器のパラメータを保持

        観測見積もり.md
            └ 誤差検討 \n
                ├ システムゲインの導出 \n
                ├ 装置透過率の導出 \n
                ├ 干渉フィルター透過率の導出 \n
                └ 装置のpixel数関連の導出 \n

        Parameters
        ----------
        telescope_params : TelescopeParameters,
            自作インスタンス
        is_ESPRIT : bool
            ESPRITか、TOPICSか。
            Falseの場合、TOPICSを想定した計算になる。
            プレートスケール、tau_iで用いる各透過率が変更される。
        N_read : float
            [e-rms] 読み出しノイズ
        I_dark : float
            [e-/s] 検出器暗電流
        G_Amp : float
            [無次元] プリアンプ倍率
        has_fiber : bool
            焦点から分光器への導入用ファイバーを使うかどうか。
            Trueの場合、l_fbなどを用いてファイバー透過率が計算される。
            Falseの場合、ファイバー透過率は自動的に1に設定される。
        l_fb : float
            [m] 分光器導入用ファイバーの長さ
        rambda_fl_center : float
            [m] フィルターの中心波長
        tau_fl_center : float
            [無次元] フィルターの中心透過率
        FWHM_fl : float
            [m] フィルターの半値全幅
        """

        # 入力されたパラメーターの代入
        self.telescope_params = telescope_params
        self.is_ESPRIT = is_ESPRIT
        self.N_read = N_read
        self.I_dark = I_dark
        self.G_Amp = G_Amp
        self.has_fiber = has_fiber
        self.l_fb = l_fb
        self.rambda_fl_center = rambda_fl_center
        self.tau_fl_center = tau_fl_center
        self.FWHM_fl = FWHM_fl

        # システムゲインの導出
        self.G_sys = self.__calc_G_sys()
        FW = 152000
        self.S_FW_pix = FW / self.G_sys

        # 各透過率の導出
        if self.has_fiber:
            self.tau_fb = self.__calc_tau_fb()
        else:
            self.tau_fb = 1

        # ピクセル数関連の導出
        f_t = self.telescope_params.f_t
        s_pix = 30e-6

        if self.is_ESPRIT:
            self.m_i_all = 1
            self.theta_pix = np.arctan(s_pix / (self.m_i_all * f_t)) * (180 / np.pi) * 3600
            w_slit = 0.7
            self.n_bin_rambda = w_slit / self.theta_pix
        else:
            self.m_i_all = 2
            self.theta_pix = np.arctan(s_pix / (self.m_i_all * f_t)) * (180 / np.pi) * 3600
            self.n_bin_rambda = 1

        self.Omega = ((self.theta_pix / 3600) * (np.pi / 180))**2

        # その他の文字の定義
        self.eta = 0.889

    def h(self):
        mkhelp(self)

    def __calc_G_sys(self):
        """システムゲインG_sysの計算

        Returns
        -------
        float
            システムゲイン
        """
        e = phys_consts.e
        G_Amp = self.G_Amp
        C_PD = 7.20e-14
        G_SF = 0.699
        ADU_ADC = 10 / 2**16

        G_sys = C_PD / (e * G_SF) * ADU_ADC / G_Amp
        return G_sys

    def __calc_tau_fb(self):
        """InF3ファイバーの透過率計算

        Returns
        -------
        float
            ファイバー部分での透過率
        """
        l_fb = self.l_fb
        tau_fb_unit = 0.98
        tau_fb_coupling = 0.5

        tau_fb = tau_fb_coupling * tau_fb_unit ** l_fb
        return tau_fb

    def calc_tau_i(self, rambda_: float) -> float:
        """装置透過率の計算

        Parameters
        ----------
        rambda_ : float
            観測対象の波長

        Returns
        -------
        float
            装置内部の透過率の合算
        """

        def calc_tau_i_filter():
            """干渉フィルターの透過率を計算

            Returns
            -------
            float
                干渉フィルターの透過率
            """
            rambda_fl_center = self.rambda_fl_center
            tau_fl_center = self.tau_fl_center
            FWHM_fl = self.FWHM_fl
            rambda__ = rambda_

            tau_i_filter = tau_fl_center \
                * np.exp(
                    - (rambda__ - rambda_fl_center)**2 / (2 * (FWHM_fl / (2 * np.sqrt(2 * np.log(2))))**2))

            return tau_i_filter

        def calc_tau_i_ESPRIT():
            """ESPRITでのtau_iを計算

            Returns
            -------
            float
                ESPRITでのtau_i
            """
            tau_i_lens = 0.66
            tau_i_mirror = 0.86
            tau_i_filter = calc_tau_i_filter()

            # 実際は回折効率は波長依存性がかなりある（宇野2012D論p106）が、ひとまず固定値として計算
            tau_i_grating = 0.66

            tau_i = tau_i_lens * tau_i_mirror * tau_i_filter * tau_i_grating
            return tau_i

        def calc_tau_i_TOPICS():
            """TOPICSでのtau_iを計算

            Returns
            -------
            float
                TOPICSでのtau_i
            """
            tau_i_lens = 0.9**3
            tau_i_filter = calc_tau_i_filter()

            tau_i = tau_i_lens * tau_i_filter
            return tau_i

        if self.is_ESPRIT:
            tau_i = calc_tau_i_ESPRIT()
        else:
            tau_i = calc_tau_i_TOPICS()

        return tau_i


class ObservationParameters:

    def __init__(
            self,
            n_bin_spatial: int,
            t_obs: float) -> None:
        """観測者が決めるパラメータを格納

        観測見積もり.md
            └ 誤差検討 \n
                ├ 装置のpixel数関連の導出 \n
                └ 観測によるSignalの導出 \n

        Parameters
        ----------
        n_bin_spatial : int
            [pix] 空間方向のbinning数、
            TOPICSなら緯度経度方向の掛け算結果を入力
            ESPRITなら空間方向1次元のbinning数を入力
        t_obs : float
            [s] 積分時間
        """

        # 入力パラメータの代入
        self.n_bin_spatial = n_bin_spatial
        self.t_obs = t_obs

    def h(self):
        mkhelp(self)


class EmissionLineDisperse:

    def __init__(
            self,
            emission_line_params,
            instrument_params,
            telescope_params,
            observation_params) -> None:
        """輝線発光を観測した時のSNRを計算

        観測見積もり.md
            └ 誤差検討 \n
                ├ 装置のpixel数関連の導出 \n
                ├ 観測によるSignalの導出 \n
                ├ その他のSignalの導出とS_allの導入 \n
                └ S/N導出とDelta_Sの導入 \n

        Parameters
        ----------
        emission_line_params : EmissionLineParameters
            インスタンス
        instrument_params : InstrumentParameters
            インスタンス
        telescope_params : TelescopeParameters
            インスタンス
        observation_params : ObservationParameters
            インスタンス
        """

        # 入力パラメータの代入
        self.emission_line_params = emission_line_params
        self.instrument_params = instrument_params
        self.telescope_params = telescope_params
        self.observation_params = observation_params

        # 装置透過率の導出
        tau_GBT = telescope_params.tau_GBT
        tau_fb = instrument_params.tau_fb
        tau_i = instrument_params.calc_tau_i(rambda_=self.emission_line_params.rambda)
        self.tau_e = tau_GBT * tau_fb * tau_i

        # 装置のpixel数関連の導出
        self.n_bin = instrument_params.n_bin_rambda * observation_params.n_bin_spatial

        # 各発光強度の導出
        self.I_obj = self.emission_line_params.I_obj
        self.I_GBT = self.telescope_params.calc_I_GBT(
            rambda_=self.emission_line_params.rambda,
            FWHM_fl=self.instrument_params.FWHM_fl)
        self.I_sky = self.telescope_params.calc_I_sky(
            rambda_=self.emission_line_params.rambda,
            FWHM_fl=self.instrument_params.FWHM_fl)

        # 各Singalの導出
        self.S_obj = self.__calc_S_xx(
            I_xx_=self.I_obj,
            tau_sky_=self.telescope_params.tau_sky)

        self.S_GBT = self.__calc_S_xx(
            I_xx_=self.I_GBT,
            tau_sky_=1)

        self.S_sky = self.__calc_S_xx(
            I_xx_=self.I_sky,
            tau_sky_=1)

        # 暗電流によるSignalの導出
        self.S_dark = self.__calc_S_dark()

        self.S_all = self.S_obj + self.S_GBT + self.S_sky + self.S_dark
        self.S_all_pix = self.S_all / self.n_bin

        # S/N導出とDelta_Sの導入
        self.SNR = self.__calc_SNR()
        self.Delta_S = self.S_obj / self.SNR

    def h(self):
        mkhelp(self)

    def __calc_S_xx(self, I_xx_: float, tau_sky_: float) -> float:
        """検出器に結像される発光強度（I_obj, I_GBT, I_sky）から得られるシグナルを計算

        Parameters
        ----------
        I_xx_ : float
            [W/m^2/sr] 発光強度
        tau_sky_ : float
            [無次元] 大気透過率、I_GBTとI_skyでは1を代入する（mdに詳細あり）

        Returns
        -------
        float
            [DN] シグナル値
        """

        I_xx = I_xx_
        A_t = self.telescope_params.A_t
        eta = self.instrument_params.eta
        Omega = self.instrument_params.Omega
        G_sys = self.instrument_params.G_sys
        tau_sky = tau_sky_
        tau_e = self.tau_e
        rambda = self.emission_line_params.rambda
        c = phys_consts.c
        h = phys_consts.h
        t_obs = self.observation_params.t_obs
        n_bin = self.n_bin

        S_xx = (I_xx * A_t * Omega * tau_sky * tau_e) \
            / (h * c / rambda) \
            * eta * (1 / G_sys) * t_obs * n_bin

        return S_xx

    def __calc_S_dark(self) -> float:
        """暗電流によるシグナルを計算

        Returns
        -------
        float
            [DN] 暗電流によるシグナル
        """
        I_dark = self.instrument_params.I_dark
        G_sys = self.instrument_params.G_sys
        t_obs = self.observation_params.t_obs
        n_bin = self.n_bin

        S_dark = (I_dark / G_sys) * t_obs * n_bin
        return S_dark

    def __calc_SNR(self) -> float:
        """SNRの計算を実装

        Returns
        -------
        float
            [無次元] SNR = S_obj / N_all
        """
        S_obj = self.S_obj
        S_GBT = self.S_GBT
        S_sky = self.S_sky
        S_dark = self.S_dark
        N_read = self.instrument_params.N_read
        G_sys = self.instrument_params.G_sys
        n_bin = self.n_bin

        N_all = np.sqrt(S_obj + S_GBT + S_sky + S_dark + (N_read / G_sys)**2 * n_bin)
        SNR = S_obj / N_all
        return SNR


class TemperatureFromSpectroscopy:

    def __init__(self, emission_disperse_FD, emission_disperse_HB) -> None:
        """2つの輝線観測結果から温度のSNRを計算

        観測見積もり.md
            ├ 観測対象の発光 \n
            │  └ 振動温度の導出 \n
            └ 観測誤差の伝搬 \n

        Parameters
        ----------
        emission_disperse_FD : EmissionLineDisperse
            インスタンス（Fundamental Band）
        emission_disperse_HB : EmissionLineDisperse
            インスタンス（Hot Band）
        """

        # 入力パラメータの代入
        self.emission_disperse_FD = emission_disperse_FD
        self.emission_disperse_HB = emission_disperse_HB

        self.beta = self.__calc_beta()
        self.R_S = self.__calc_R_S()
        self.T_vib = self.__calc_T_vib()
        self.Delta_R_S = self.__calc_Delta_R_S()
        self.Delta_T = self.__calc_Delta_T()
        self.SNR_T = self.T_vib / self.Delta_T

    def h(self):
        mkhelp(self)

    def __calc_beta(self):
        g_ns_FD = self.emission_disperse_FD.emission_line_params.g_ns
        J_prime_FD = self.emission_disperse_FD.emission_line_params.J_prime
        omega_if_FD = self.emission_disperse_FD.emission_line_params.omega_if
        A_if_FD = self.emission_disperse_FD.emission_line_params.A_if

        g_ns_HB = self.emission_disperse_HB.emission_line_params.g_ns
        J_prime_HB = self.emission_disperse_HB.emission_line_params.J_prime
        omega_if_HB = self.emission_disperse_HB.emission_line_params.omega_if
        A_if_HB = self.emission_disperse_HB.emission_line_params.A_if

        beta = (g_ns_HB * (2 * J_prime_HB + 1) * omega_if_HB * A_if_HB) \
            / (g_ns_FD * (2 * J_prime_FD + 1) * omega_if_FD * A_if_FD)

        return beta

    def __calc_R_S(self):
        S_HB = self.emission_disperse_HB.S_obj
        S_FD = self.emission_disperse_FD.S_obj

        R_S = S_HB / S_FD
        return R_S

    def __calc_T_vib(self):
        E_prime_FD = self.emission_disperse_FD.emission_line_params.E_prime
        E_prime_HB = self.emission_disperse_HB.emission_line_params.E_prime
        h = phys_consts.h
        c = phys_consts.c
        k_B = phys_consts.k
        beta = self.beta
        R_S = self.R_S

        T_vib = (h * c / k_B) * (E_prime_HB - E_prime_FD) * 1e2 / (np.log(beta) - np.log(R_S))
        return T_vib

    def __calc_Delta_R_S(self):
        S_FD = self.emission_disperse_FD.S_obj
        S_HB = self.emission_disperse_HB.S_obj
        Delta_S_FD = self.emission_disperse_FD.Delta_S
        Delta_S_HB = self.emission_disperse_HB.Delta_S

        Delta_R_S = np.sqrt((Delta_S_HB / S_FD)**2 + (S_HB * Delta_S_FD / S_FD**2)**2)
        return Delta_R_S

    def __calc_Delta_T(self):
        E_prime_FD = self.emission_disperse_FD.emission_line_params.E_prime
        E_prime_HB = self.emission_disperse_HB.emission_line_params.E_prime
        h = phys_consts.h
        c = phys_consts.c
        k_B = phys_consts.k
        beta = self.beta
        R_S = self.R_S
        Delta_R_S = self.Delta_R_S

        del_T_del_R_S = - h * c / k_B \
            * (E_prime_HB - E_prime_FD) * 1e2 \
            / (np.log(beta) - np.log(R_S))**2 \
            * (1 / R_S)

        Delta_T = np.abs(del_T_del_R_S * Delta_R_S)

        return Delta_T
