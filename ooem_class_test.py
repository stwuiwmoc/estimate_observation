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
    column_density_H3plus = 2.0e+16  # [/m^2] H3+カラム密度
    T_thermospheric_H3plus = 1200  # [K] H3+熱圏温度
    t_obs = 15  # [s] 積分時間
    n_bin_spatial = 3

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

    Haleakala_Oct_good = ooem.EarthAtmosphere(
        T_ATM=273,
        ATRAN_result_filepath="raw_data/Ha_PWV2000_ZA22_Range3to4_R0.txt")

    T60 = ooem.GroundBasedTelescope(
        D_GBT=0.6,
        FNO_GBT=12,
        T_GBT=280,
        tau_GBT=0.66)

    TOPICS = ooem.ImagingInstrument(
        rambda_BPF_center=3.414e-6,
        FWHM_BPF=17e-9,
        tau_BPF_center=0.88,
        tau_i_ND=1,
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
    print("Only R_3_0 emission, I =", light_all.get_I())

    R_3_1.add_auroral_emission_to(light_instance=light_all)

    R_3_2.add_auroral_emission_to(light_instance=light_all)

    R_3_3.add_auroral_emission_to(light_instance=light_all)

    R_4_3.add_auroral_emission_to(light_instance=light_all)

    R_4_4.add_auroral_emission_to(light_instance=light_all)
    ax11 = light_all.show_rambda_vs_I_prime_plot(fig=fig1, position=gs1[0, 0])

    # 地球大気を通る
    Haleakala_Oct_good.pass_through(light_instance=light_all)
    Haleakala_Oct_good.pass_through(light_instance=light_sky)
    ax12 = light_all.show_rambda_vs_I_prime_plot(fig=fig1, position=gs1[1, 0])

    # 望遠鏡を通る
    T60.pass_through(light_instance=light_all)
    T60.pass_through(light_instance=light_sky)
    ax13 = light_all.show_rambda_vs_I_prime_plot(fig=fig1, position=gs1[2, 0])

    # 望遠鏡への撮像装置の設置
    TOPICS.set_ImagingInstrument_to(GBT_instance=T60)

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

    # plot
    ax11.set_title("H3+ emission lines")
    ax12.set_title("pass thruogh Earth Atmosphre")
    ax13.set_title("Pass through Ground-based-telescope")
    ax14.set_title("Pass through imaging instrument")

    parametar_table_list = [
        ooem.get_latest_commit_datetime(),
        ["Have some change", "from above commit", ooem.have_some_change_in_git_status()],
        ["", "", ""],
        ["EarthAtmosphre", "", ""],
        ["ATRAN result filename", Haleakala_Oct_good.get_ATRAN_result_filepath()[9:24], Haleakala_Oct_good.get_ATRAN_result_filepath()[24:]],
        ["T_ATM", Haleakala_Oct_good.get_T_ATM(), "K"],
        ["", "", ""],
        ["GroundBasedTelescope", "", ""],
        ["D_GBT", T60.get_D_GBT(), "m"],
        ["FNO_GBT", T60.get_FNO_GBT(), ""],
        ["T_GBT", T60.get_T_GBT(), "K"],
        ["", "", ""],
        ["ImagingInstrument", "", ""],
        ["rambda_BPF_center", TOPICS.get_rambda_BPF_center(), "m"],
        ["FWHM_BPF", TOPICS.get_FWHM_BPF(), "m"],
        ["tau_BPF_center", TOPICS.get_tau_BPF_center(), ""],
        ["tau_i_ND", TOPICS.get_tau_i_ND(), ""],
        ["I_dark_pix", TOPICS.get_I_dark(), "e- / s"],
        ["N_e_read_pix", TOPICS.get_N_e_read(), "e-rms"],
        ["", "", ""],
        ["Other parameters", "", ""],
        ["t_obs", t_obs, "s"],
        ["n_bin_spatial", n_bin_spatial, "pix"],
        ["", "", ""],
        ["Results", "", ""],
        ["S_all_pix (obj image)", fits_all.get_S_all_pix(), "DN / pix"],
        ["S_all_pix (sky image)", fits_sky.get_S_all_pix(), "DN / pix"],
        ["S_dark_pix", fits_all.get_S_dark_pix(), "DN / pix"],
        ["S_read_pix", fits_all.get_S_read_pix(), "DN / pix"],
        ["R_electron/FW", fits_all.get_R_electron_FW(), ""],
        ["spatial_resolution", SNRCalc.calc_spatial_resolution_for(n_bin_spatial=n_bin_spatial), "arcsec"],
        ["SNR", SNRCalc.calc_SNR_for(n_bin_spatial=n_bin_spatial), ""],
    ]

    ax15 = ooem.plot_parameter_table(
        fig=fig1, position=gs1[:, 1], parameter_table=parametar_table_list, fontsize=12)

    fig1.tight_layout()
    fig1.savefig(mkfolder() + "fig1.png")
