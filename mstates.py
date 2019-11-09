import mne
import microstates
import numpy as np
import matplotlib.pyplot as plt

subj = 1
nstates = 4
normalize = True

def myplot_maps(maps, info):
    """Plot prototypical microstate maps.

    Parameters
    ----------
    maps : ndarray, shape (n_channels, n_maps)
        The prototypical microstate maps.
    info : instance of mne.io.Info
        The info structure of the dataset, containing the location of the
        sensors.
    """
    #plt.figure(figsize=(2 * len(maps), 2))
    layout = mne.channels.find_layout(info)
    for i, map in enumerate(maps):
        plt.subplot(1, len(maps), i + 1)
        mne.viz.plot_topomap(map, layout.pos[:, :2], show=False)
        plt.title('%d' % i)



if subj == 1:
    raw = mne.io.read_raw_brainvision("../s1/BrainVision/20191029-134633-raw.Export.clean.vhdr", preload=True)
    outfile = "Maps_4states_s1.txt"
elif subj == 2:
    raw = mne.io.read_raw_brainvision("../S2 clean data/20191029-140241-raw.FinalClean.vhdr", preload=True)
    outfile = "Maps_4states_s2.txt"
elif subj ==3:
    raw = mne.io.read_raw_brainvision("../s3 clean data/20191029-141906-raw.CleanCleanClean.vhdr", preload=True)
    outfile = "Maps_4states_s3.txt"

raw.set_montage('standard_1005')
#raw.plot_sensors(show_names=True)

print(raw.info)

print(raw.annotations)

# Always use an average EEG reference when doing microstate analysis
raw.set_eeg_reference('average')


#raw.plot_psd()
plt.show()


# Highpass filter the data a little bit
raw.filter(0.2, None)

# Selecting the sensor types to use in the analysis. In this example, we
# use only EEG channels
raw.pick_types(meg=False, eeg=True)

# Segment the data into 6 microstates
maps, segmentation = microstates.segment(raw.get_data(), n_states=nstates, max_n_peaks=10000000000, max_iter=5000, normalize=normalize)

# Plot the topographic maps of the found microstates
#microstates.plot_maps(maps, raw.info)
myplot_maps(maps, raw.info)

# Plot the segmentation of the first 500 samples
cutpoint = 5000
microstates.plot_segmentation(segmentation[cutpoint-1000:cutpoint], raw.get_data()[:, cutpoint-1000:cutpoint], raw.times[cutpoint-1000:cutpoint])
plt.show()

np.savetxt(outfile, maps, delimiter=" ")
