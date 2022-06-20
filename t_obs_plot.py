# %%
import numpy as np
import matplotlib.pyplot as plt
import importlib

import observation_simulation_myclass as osm


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
    importlib.reload(osm)
    t_obs_array = np.arange(1, 100)  # [s]

    R_3_0 = osm.EmissionLineParameters(
        rambda=3.4128e-6,
        N_H3p=2.0e+16,
        g_ns=4,
        J_prime=4,
        A_if=177.6,
        E_prime=3382.9299,
        T_hypo=1200)

    TOPICS = osm.InstrumentParameters(
        is_ESPRIT=False,
        N_read=100,
        I_dark=20,
        G_Amp=9,
        has_fiber=False,
        l_fb=None,
        rambda_fl_center=3.414e-6,
        tau_fl_center=0.9,
        FWHM_fl=17e-9)

    T60_PWV2000 = osm.TelescopeParameters(
        T_GBT=273,
        telescope_diameter=0.6,
        tau_GBT=0.66,
        T_sky=273,
        tau_sky=0.744)

    T60_PWV5000 = osm.TelescopeParameters(
        T_GBT=273,
        telescope_diameter=0.6,
        tau_GBT=0.66,
        T_sky=273,
        tau_sky=0.564)

    obs_1bin = osm.ObservationParameters(
        n_bin_spatial=1,
        t_obs=t_obs_array)

    obs_4bin = osm.ObservationParameters(
        n_bin_spatial=2 * 2,
        t_obs=t_obs_array)

    obs_16bin = osm.ObservationParameters(
        n_bin_spatial=4 * 4,
        t_obs=t_obs_array)

    result_1bin_T60_PWV2000 = osm.EmissionLineDisperse(
        emission_line_params=R_3_0,
        instrument_params=TOPICS,
        telescope_params=T60_PWV2000,
        observation_params=obs_1bin)

    result_1bin_T60_PWV5000 = osm.EmissionLineDisperse(
        emission_line_params=R_3_0,
        instrument_params=TOPICS,
        telescope_params=T60_PWV5000,
        observation_params=obs_1bin)

    result_4bin_T60_PWV2000 = osm.EmissionLineDisperse(
        emission_line_params=R_3_0,
        instrument_params=TOPICS,
        telescope_params=T60_PWV2000,
        observation_params=obs_4bin)

    result_4bin_T60_PWV5000 = osm.EmissionLineDisperse(
        emission_line_params=R_3_0,
        instrument_params=TOPICS,
        telescope_params=T60_PWV5000,
        observation_params=obs_4bin)

    # plot start
    fig1 = plt.figure(figsize=(12, 10))
    gs1 = fig1.add_gridspec(2, 2)
    fig1.suptitle("T60, PWV=2000")

    # data table plot
    fig1_table_text_list = [
        ["H3+ parameters", "", ""],
        ["rambda", R_3_0.rambda, "m"],
        ["N_H3p", R_3_0.N_H3p, "m^-2"],
        ["T_hypo", R_3_0.T_hypo, "K"],
        ["", "", ""],
        ["Telescope parameters", "", ""],
        ["telescope_diameter", T60_PWV2000.telescope_diameter, "m"],
        ["T_GBT", T60_PWV2000.T_GBT, "K"],
        ["tau_GBT", T60_PWV2000.tau_GBT, ""],
        ["T_sky", T60_PWV2000.T_sky, "K"],
        ["tau_sky", T60_PWV2000.tau_sky, ""],
        ["", "", ""],
        ["Observation_parameters", "", ""],
        ["t_obs", "", "s"],
        ["", "", ""],
        ["Intensity", "", ""],
        ["I_obj", result_1bin_T60_PWV2000.I_obj, "W / m^2 / str"],
        ["I_sky", result_1bin_T60_PWV2000.I_sky, "W / m^2 / str"],
        ["I_GBT", result_1bin_T60_PWV2000.I_GBT, "W / m^2 / str"],
        ["", "", ""],
        ["Instrument parameters", "", ""],
        ["N_read", TOPICS.N_read, "e-rms"],
        ["I_dark", TOPICS.I_dark, "e-/s"],
        ["rambda_fl_center", TOPICS.rambda_fl_center, "m"],
        ["tau_fl_center", TOPICS.tau_fl_center, ""],
        ["FWHM_fl", TOPICS.FWHM_fl, "m"]]

    ax13 = osm.plot_parameter_table(
        fig=fig1,
        position=gs1[0:2, 1],
        parameter_table=fig1_table_text_list,
        fontsize=8)

    # t_obs vs e- plot
    ax11 = fig1.add_subplot(gs1[0, 0])

    # Signal plot
    linestyle_signal = "-"
    linewidth_signal = 3

    ax11.plot(
        t_obs_array,
        result_1bin_T60_PWV2000.S_all * TOPICS.G_sys,
        label="S_all",
        linestyle=linestyle_signal,
        linewidth=linewidth_signal)
    ax11.plot(
        t_obs_array,
        result_1bin_T60_PWV2000.S_obj * TOPICS.G_sys,
        label="S_obj",
        linestyle=linestyle_signal,
        linewidth=linewidth_signal)

    # Noise plot
    linestyle_noise = "-."
    ax11.plot(
        t_obs_array,
        np.sqrt(result_1bin_T60_PWV2000.S_all * TOPICS.G_sys),
        label="N_all",
        linestyle=linestyle_noise)
    ax11.plot(
        t_obs_array,
        np.sqrt(result_1bin_T60_PWV2000.S_sky * TOPICS.G_sys),
        label="N_sky",
        linestyle=linestyle_noise)
    ax11.plot(
        t_obs_array,
        np.sqrt(result_1bin_T60_PWV2000.S_GBT * TOPICS.G_sys),
        label="N_GBT",
        linestyle=linestyle_noise)
    ax11.plot(
        t_obs_array,
        np.sqrt(result_1bin_T60_PWV2000.S_dark * TOPICS.G_sys),
        label="N_dark",
        linestyle=linestyle_noise)
    ax11.plot(
        t_obs_array,
        TOPICS.N_read * np.ones(len(t_obs_array)),
        label="N_read",
        linestyle=linestyle_noise)

    # FullWell plot
    ax11.plot(
        t_obs_array,
        TOPICS.S_FW_pix * TOPICS.G_sys * np.ones(len(t_obs_array)),
        label="FW limit",
        linestyle=":",
        linewidth=3)

    # axes decoration
    ax11.grid(axis="x", which="major")
    ax11.grid(axis="y", which="major")

    ax11.set_xlabel("Integration Time t_obs [s]")
    ax11.set_ylabel("Signal and Noise per 1 pixel [e-]")

    ax11.set_xscale("log")
    ax11.set_yscale("log")

    ax11.legend()

    # t_obs vs SNR plot
    ax12 = fig1.add_subplot(gs1[1, 0])

    # SNR plot
    ax12.plot(
        t_obs_array,
        result_1bin_T60_PWV2000.SNR,
        label=str(result_1bin_T60_PWV2000.n_bin) + " pix binning")
    ax12.plot(
        t_obs_array,
        result_4bin_T60_PWV2000.SNR,
        label=str(result_4bin_T60_PWV2000.n_bin) + " pix binning")

    ax12.grid()

    ax12.set_xlabel("Integration Time t_obs [s]")
    ax12.set_ylabel("SNR of each binning number")

    ax12.set_xscale("log")

    ax12.legend()

    fig1.tight_layout()

    fig1.savefig(mkfolder() + "fig1.png")

    # plot start
    fig2 = plt.figure(figsize=(12, 10))
    gs1 = fig2.add_gridspec(2, 2)
    fig2.suptitle("T60, PWV=5000")

    # data table plot
    fig2_table_text_list = [
        ["H3+ parameters", "", ""],
        ["rambda", R_3_0.rambda, "m"],
        ["N_H3p", R_3_0.N_H3p, "m^-2"],
        ["T_hypo", R_3_0.T_hypo, "K"],
        ["", "", ""],
        ["Telescope parameters", "", ""],
        ["telescope_diameter", T60_PWV5000.telescope_diameter, "m"],
        ["T_GBT", T60_PWV5000.T_GBT, "K"],
        ["tau_GBT", T60_PWV5000.tau_GBT, ""],
        ["T_sky", T60_PWV5000.T_sky, "K"],
        ["tau_sky", T60_PWV5000.tau_sky, ""],
        ["", "", ""],
        ["Observation_parameters", "", ""],
        ["t_obs", "", "s"],
        ["", "", ""],
        ["Intensity", "", ""],
        ["I_obj", result_1bin_T60_PWV5000.I_obj, "W / m^2 / str"],
        ["I_sky", result_1bin_T60_PWV5000.I_sky, "W / m^2 / str"],
        ["I_GBT", result_1bin_T60_PWV5000.I_GBT, "W / m^2 / str"],
        ["", "", ""],
        ["Instrument parameters", "", ""],
        ["N_read", TOPICS.N_read, "e-rms"],
        ["I_dark", TOPICS.I_dark, "e-/s"],
        ["rambda_fl_center", TOPICS.rambda_fl_center, "m"],
        ["tau_fl_center", TOPICS.tau_fl_center, ""],
        ["FWHM_fl", TOPICS.FWHM_fl, "m"]]

    ax23 = osm.plot_parameter_table(
        fig=fig2,
        position=gs1[0:2, 1],
        parameter_table=fig2_table_text_list,
        fontsize=8)

    # t_obs vs e- plot
    ax21 = fig2.add_subplot(gs1[0, 0])

    # Signal plot
    linestyle_signal = "-"
    linewidth_signal = 3

    ax21.plot(
        t_obs_array,
        result_1bin_T60_PWV5000.S_all * TOPICS.G_sys,
        label="S_all",
        linestyle=linestyle_signal,
        linewidth=linewidth_signal)
    ax21.plot(
        t_obs_array,
        result_1bin_T60_PWV5000.S_obj * TOPICS.G_sys,
        label="S_obj",
        linestyle=linestyle_signal,
        linewidth=linewidth_signal)

    # Noise plot
    linestyle_noise = "-."
    ax21.plot(
        t_obs_array,
        np.sqrt(result_1bin_T60_PWV5000.S_all * TOPICS.G_sys),
        label="N_all",
        linestyle=linestyle_noise)
    ax21.plot(
        t_obs_array,
        np.sqrt(result_1bin_T60_PWV5000.S_sky * TOPICS.G_sys),
        label="N_sky",
        linestyle=linestyle_noise)
    ax21.plot(
        t_obs_array,
        np.sqrt(result_1bin_T60_PWV5000.S_GBT * TOPICS.G_sys),
        label="N_GBT",
        linestyle=linestyle_noise)
    ax21.plot(
        t_obs_array,
        np.sqrt(result_1bin_T60_PWV5000.S_dark * TOPICS.G_sys),
        label="N_dark",
        linestyle=linestyle_noise)
    ax21.plot(
        t_obs_array,
        TOPICS.N_read * np.ones(len(t_obs_array)),
        label="N_read",
        linestyle=linestyle_noise)

    # FullWell plot
    ax21.plot(
        t_obs_array,
        TOPICS.S_FW_pix * TOPICS.G_sys * np.ones(len(t_obs_array)),
        label="FW limit",
        linestyle=":",
        linewidth=3)

    # axes decoration
    ax21.grid(axis="x", which="major")
    ax21.grid(axis="y", which="major")

    ax21.set_xlabel("Integration Time t_obs [s]")
    ax21.set_ylabel("Signal and Noise per 1 pixel [e-]")

    ax21.set_xscale("log")
    ax21.set_yscale("log")

    ax21.legend()

    # t_obs vs SNR plot
    ax22 = fig2.add_subplot(gs1[1, 0])

    # SNR plot
    ax22.plot(
        t_obs_array,
        result_1bin_T60_PWV5000.SNR,
        label=str(result_1bin_T60_PWV5000.n_bin) + " pix binning")
    ax22.plot(
        t_obs_array,
        result_4bin_T60_PWV5000.SNR,
        label=str(result_4bin_T60_PWV5000.n_bin) + " pix binning")

    ax22.grid()

    ax22.set_xlabel("Integration Time t_obs [s]")
    ax22.set_ylabel("SNR of each binning number")

    ax22.set_xscale("log")

    ax22.legend()

    fig2.tight_layout()

    fig2.savefig(mkfolder() + "fig2.png")
