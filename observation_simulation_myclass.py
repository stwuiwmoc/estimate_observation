# %%
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

        A_0 = -1.11391
        A_1 = +0.0581076
        A_2 = +0.000302967
        A_3 = -2.83724e-7
        A_4 = +2.31119e-10
        A_5 = -7.15895e-14
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


class InstrumentParameters:

    def __init__(
            self, N_read, I_dark, G_Amp, l_f, telescope_diameter) -> None:

        # 入力されたパラメーターの代入
        self.N_read = N_read
        self.I_dark = I_dark
        self.G_Amp = G_Amp
        self.l_f = l_f
        self.telescope_diameter = telescope_diameter

        # システムゲインの導出
        self.G_sys = self.__calc_G_sys()

        # 装置透過率の導出
        self.tau_t = 0.66
        self.tau_f = self.__calc_tau_f()
        self.tau_s = self.__calc_tau_s()
        self.tau_e = self.tau_t * self.tau_f * self.tau_s

        # ピクセル数関連の導出
        s_plate = 0.3  # <-ESPRITの値 プレートスケールは検出器までの光学系依存なのでTOPICSでは値が変わることに注意
        self.Omega = 2.35e-11 * s_plate
        w_slit = 0.7
        self.n_pix = w_slit / s_plate

        # その他の文字の定義
        self.A_t = np.pi * (self.telescope_diameter / 2) ** 2
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

    def __calc_tau_f(self):
        """InF3ファイバーの透過率計算

        Returns
        -------
        float
            ファイバー部分での透過率
        """
        l_f = self.l_f
        tau_f_unit = 0.98
        tau_f_coupling = 0.5

        tau_f = tau_f_coupling * tau_f_unit ** l_f
        return tau_f

    def __calc_tau_s(self):
        """ESPRITの装置透過率の計算

        Returns
        -------
        float
            ESPRIT全体での装置透過率
        """
        tau_s_lens = 0.66
        tau_s_mirror = 0.86

        # 実際は回折効率は波長依存性がかなりある（宇野2012D論p106）が、ひとまず固定値として計算
        tau_s_grating = 0.66

        tau_s = tau_s_lens * tau_s_mirror * tau_s_grating
        return tau_s


class ObservationParameters:

    def __init__(self, t_obs) -> None:

        # 入力パラメータの代入
        self.t_obs = t_obs
        self.tau_alpha = 0.9

        # 参照元に I_GBT + I_sky のみの合算値しかないので、実装では md上の $I_{GBT} + I_{sky}$ を I_GBT_sky として記述
        self.I_GBT_sky = 2.99e-6  # ESPRIT 3.4umでの値を仮置きした、今後もう少し複雑な機能を実装するかも

    def h(self):
        mkhelp(self)


class EmissionLineDisperse:

    def __init__(
            self,
            emission_line_params,
            instrument_params,
            observation_params) -> None:

        # 入力パラメータの代入
        self.emission_line_params = emission_line_params
        self.instrument_params = instrument_params
        self.observation_params = observation_params

        # 各Singalの導出
        self.S_obj = self.__calc_S_xx(
            I_xx_=self.emission_line_params.I_obj,
            tau_alpha_=self.observation_params.tau_alpha)

        self.S_GBT_sky = self.__calc_S_xx(
            I_xx_=self.observation_params.I_GBT_sky,
            tau_alpha_=1)

        # 暗電流によるSignalの導出
        self.S_dark = self.__calc_S_dark()

        # S/N導出とDelta_Sの導入
        self.SNR = self.__calc_SNR()
        self.Delta_S = self.S_obj / self.SNR

    def h(self):
        mkhelp(self)

    def __calc_S_xx(self, I_xx_: float, tau_alpha_: float) -> float:
        """検出器に結像される発光強度（I_obj, I_GBT, I_sky）から得られるシグナルを計算

        Parameters
        ----------
        I_xx_ : float
            [W/m^2/str] 発光強度
        tau_alpha_ : float
            [無次元] 大気透過率、I_GBTとI_skyでは1を代入する（mdに詳細あり）

        Returns
        -------
        float
            [DN] シグナル値
        """

        I_xx = I_xx_
        A_t = self.instrument_params.A_t
        eta = self.instrument_params.eta
        Omega = self.instrument_params.Omega
        G_sys = self.instrument_params.G_sys
        tau_alpha = tau_alpha_
        tau_e = self.instrument_params.tau_e
        rambda = self.emission_line_params.rambda
        c = phys_consts.c
        h = phys_consts.h
        t_obs = self.observation_params.t_obs
        n_pix = self.instrument_params.n_pix

        S_xx = (I_xx * A_t * Omega * tau_alpha * tau_e) \
            / (h * c / rambda) \
            * eta * (1 / G_sys) * t_obs * n_pix

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
        n_pix = self.instrument_params.n_pix

        S_dark = (I_dark / G_sys) * t_obs * n_pix
        return S_dark

    def __calc_SNR(self) -> float:
        """SNRの計算を実装

        Returns
        -------
        float
            [無次元] SNR = S_obj / N_all
        """
        S_obj = self.S_obj
        S_GBT_sky = self.S_GBT_sky
        S_dark = self.S_dark
        N_read = self.instrument_params.N_read
        G_sys = self.instrument_params.G_sys
        n_pix = self.instrument_params.n_pix

        N_all = np.sqrt(S_obj + S_GBT_sky + S_dark + (N_read / G_sys)**2 * n_pix)
        SNR = S_obj / N_all
        return SNR


class TemperatureFromSpectroscopy:

    def __init__(self, emission_disperse_FD, emission_disperse_HB) -> None:
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
