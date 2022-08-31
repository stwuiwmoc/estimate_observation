# %%
import importlib

import matplotlib.pyplot as plt

import object_oriented_estimation_myclass as ooem


def mkfolder(suffix=""):
    import os
    """
    Parameters
    ----------
    suffix : str, optional
        The default is "".

    Returns
    -------
    str ( script name + suffix )
    """
    filename = os.path.basename(__file__)
    filename = filename.replace(".py", "") + suffix
    folder = "mkfolder/" + filename + "/"
    os.makedirs(folder, exist_ok=True)
    return folder


if __name__ == "__main__":
    importlib.reload(ooem)

    # グローバル変数の定義
    column_density_H3plus = 1.5e+16  # [/m^2] H3+カラム密度
    T_thermospheric_H3plus = 1200  # [K] H3+熱圏温度
    t_obs = 12.5  # [s] 積分時間
    n_bin_spatial_list = [10, 14, 20]

    # 各インスタンス生成
    light_all = ooem.LightGenenrator(
        rambda_division_width=0.1e-9,
        rambda_lower_limit=3.3e-6,
        rambda_upper_limit=3.5e-6)

    light_sky = ooem.LightGenenrator(
        rambda_division_width=0.1e-9,
        rambda_lower_limit=3.3e-6,
        rambda_upper_limit=3.5e-6)

    R_3_0 = ooem.H3plusAuroralEmission(
        rambda_obj=3.4128e-6,
        N_H3p=column_density_H3plus,
        g_ns=4,
        J_prime=4,
        A_if=177.6,
        E_prime=3382.9299,
        T_hypo=T_thermospheric_H3plus)

    R_3_1 = ooem.H3plusAuroralEmission(
        rambda_obj=3.4149e-6,
        N_H3p=column_density_H3plus,
        g_ns=2,
        J_prime=4,
        A_if=110.4,
        E_prime=3359.002,
        T_hypo=T_thermospheric_H3plus)

    R_3_2 = ooem.H3plusAuroralEmission(
        rambda_obj=3.4207e-6,
        N_H3p=column_density_H3plus,
        g_ns=2,
        J_prime=4,
        A_if=86.91,
        E_prime=3287.2629,
        T_hypo=T_thermospheric_H3plus)

    R_3_3 = ooem.H3plusAuroralEmission(
        rambda_obj=3.4270e-6,
        N_H3p=column_density_H3plus,
        g_ns=4,
        J_prime=4,
        A_if=42.94,
        E_prime=3169.252,
        T_hypo=T_thermospheric_H3plus)

    R_4_3 = ooem.H3plusAuroralEmission(
        rambda_obj=3.4547e-6,
        N_H3p=column_density_H3plus,
        g_ns=4,
        J_prime=5,
        A_if=62.91,
        E_prime=3489.2151,
        T_hypo=T_thermospheric_H3plus)

    R_4_4 = ooem.H3plusAuroralEmission(
        rambda_obj=3.4548e-6,
        N_H3p=column_density_H3plus,
        g_ns=2,
        J_prime=5,
        A_if=122.9,
        E_prime=3332.4121,
        T_hypo=T_thermospheric_H3plus)

    Nayoro_Oct = ooem.EarthAtmosphere(
        T_ATM=273,
        ATRAN_result_filepath="raw_data/Na_PWV8000_ZA46_Range3to4_R0.txt")

    Pirika = ooem.GroundBasedTelescope(
        D_GBT=1.6,
        FNO_GBT=12,
        T_GBT=268,
        tau_GBT=0.8**3)

    TOPICS = ooem.ImagingInstrument(
        rambda_fl_center=3.414e-6,
        FWHM_fl=17e-9,
        tau_fl_center=0.88,
        G_Amp=9,
        I_dark=50,
        N_e_read=1200)

    fits_all = ooem.VirtualOutputFileGenerator()
    fits_sky = ooem.VirtualOutputFileGenerator()

    SNRCalc = ooem.SNRCalculator(
        all_image_instance=fits_all,
        sky_image_instance=fits_sky)

    # plot作成の準備
    fig1 = plt.figure(figsize=(15, 15))
    gs1 = fig1.add_gridspec(4, 2)

    # 輝線発光を加える
    R_3_0.add_auroral_emission_to(light_instance=light_all)
    R_3_1.add_auroral_emission_to(light_instance=light_all)
    R_3_2.add_auroral_emission_to(light_instance=light_all)
    R_3_3.add_auroral_emission_to(light_instance=light_all)
    R_4_3.add_auroral_emission_to(light_instance=light_all)
    R_4_4.add_auroral_emission_to(light_instance=light_all)

    ax11 = light_all.show_rambda_vs_I_prime_plot(fig=fig1, position=gs1[0, 0])

    # 地球大気を通る
    Nayoro_Oct.pass_through(light_instance=light_all)
    Nayoro_Oct.pass_through(light_instance=light_sky)
    ax12 = light_all.show_rambda_vs_I_prime_plot(fig=fig1, position=gs1[1, 0])

    # 望遠鏡を通る
    Pirika.pass_through(light_instance=light_all)
    Pirika.pass_through(light_instance=light_sky)
    ax13 = light_all.show_rambda_vs_I_prime_plot(fig=fig1, position=gs1[2, 0])

    # 望遠鏡への撮像装置の設置
    TOPICS.set_ImagingInstrument_to(GBT_instance=Pirika)

    # 撮像してfitsに保存
    TOPICS.shoot_light_and_save_to_fits(
        light_instance=light_all,
        virtual_output_file_instance=fits_all,
        t_obs=t_obs)
    TOPICS.shoot_light_and_save_to_fits(
        light_instance=light_sky,
        virtual_output_file_instance=fits_sky,
        t_obs=t_obs)

    ax14 = light_all.show_rambda_vs_I_prime_plot(fig=fig1, position=gs1[3, 0])

    # binning数を変えた時の空間分解能とSNRを表示
    for i in range(len(n_bin_spatial_list)):
        print(
            "n_bin_spatial =",
            n_bin_spatial_list[i],
            ", spatial_resolution =",
            SNRCalc.calc_spatial_resolution_for(n_bin_spatial=n_bin_spatial_list[i]),
            ", SNR =",
            SNRCalc.calc_SNR_for(n_bin_spatial=n_bin_spatial_list[i]))

    # plot
    ax11.set_title("H3+ emission lines")
    ax12.set_title("pass thruogh Earth Atmosphre")
    ax13.set_title("Pass through Ground-based-telescope")
    ax14.set_title("Pass through imaging instrument")

    parametar_table_list = [
        ooem.get_latest_commit_datetime(),
        ["Have some change", "from above commit", ooem.have_some_change_in_git_status()],
        ["", "", ""],
        ["H3plusEmission", "", ""],
        ["N_H3+", R_3_0.get_N_H3p(), "/ m^2"],
        ["T_hypo", R_3_0.get_T_hypo(), "K"],
        ["", "", ""],
        ["EarthAtmosphre", "", ""],
        ["ATRAN result filename", Nayoro_Oct.get_ATRAN_result_filepath()[9:25], Nayoro_Oct.get_ATRAN_result_filepath()[25:]],
        ["T_ATM", Nayoro_Oct.get_T_ATM(), "K"],
        ["", "", ""],
        ["GroundBasedTelescope", "", ""],
        ["D_GBT", Pirika.get_D_GBT(), "m"],
        ["FNO_GBT", Pirika.get_FNO_GBT(), ""],
        ["tau_GBT", Pirika.get_tau_GBT(), "K"],
        ["T_GBT", Pirika.get_T_GBT(), "K"],
        ["", "", ""],
        ["ImagingInstrument", "", ""],
        ["rambda_fl_center", TOPICS.get_rambda_fl_center(), "m"],
        ["FWHM_fl", TOPICS.get_FWHM_fl(), "m"],
        ["tau_fl_center", TOPICS.get_tau_fl_center(), ""],
        ["I_dark_pix", TOPICS.get_I_dark(), "e- / s"],
        ["N_e_read_pix", TOPICS.get_N_e_read(), "e-rms"],
        ["", "", ""],
        ["Other parameters", "", ""],
        ["t_obs", t_obs, "s"],
        ["n_bin_spatial", n_bin_spatial_list[0], "pix"],
        ["Field of View", TOPICS.get_theta_pix() * 256, "arcsec"],
        ["spatial_resolution", SNRCalc.calc_spatial_resolution_for(n_bin_spatial=n_bin_spatial_list[0]), "arcsec"],
        ["", "", ""],
        ["Results", "", ""],
        ["S_all_pix", fits_all.get_S_all_pix(), "DN / pix"],
        ["S_dark_pix", fits_all.get_S_dark_pix(), "DN / pix"],
        ["S_read_pix", fits_all.get_S_read_pix(), "DN / pix"],
        ["R_electron/FW", fits_all.get_R_electron_FW(), ""],
        ["SNR", SNRCalc.calc_SNR_for(n_bin_spatial=n_bin_spatial_list[0]), ""],
    ]

    ax15 = ooem.plot_parameter_table(
        fig=fig1, position=gs1[:, 1], parameter_table=parametar_table_list, fontsize=12)

    fig1.suptitle("H3+ 3.4um in Nayoro")
    fig1.tight_layout()
    fig1.savefig(mkfolder() + "fig1.png")