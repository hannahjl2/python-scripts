import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import h5py
from mpl_toolkits.axes_grid1 import make_axes_locatable

mp = 1.672622e-24 # mass of hydrogren atom, in grams
kb = 1.380658e-16 # boltzmann constant in ergs/K

DE = 0 # Dual Energy Flag

dnamein='../../data/cloud_wind/2/' # directory where the file is located
dnameout='../../data/cloud_wind/2/Tslices/' # directory where the plot will be saved

sims = ['128/', '256/', '512/', '1024/']
labels = ['$R_{4}$', '$R_{8}$', '$R_{16}$', '$R_{32}$']
cat = [False, False, True, True]

t_cc = 4.89e3 # cloud crushing time in kyr
iend = 500

for i in range(iend):

    fig, axs = plt.subplots(nrows=len(sims), ncols=1)
    fig_color = 'white'
    bg_color = 'black'

    for j in range(len(sims)):
        if cat[j]:
            f = h5py.File(dnamein + sims[j] + 'hdf5/' +str(i) + '_slice.h5', 'r') 
        else:
            f = h5py.File(dnamein + sims[j] + 'hdf5/' +str(i) + '_slice.h5.0', 'r') 
        head = f.attrs # read the header attributes into a structure, called head

        gamma = head['gamma'] # ratio of specific heats
        t  = head['t'] # time of this snapshot, in kyr
        nx = head['dims'][0] # number of cells in the x direction
        ny = head['dims'][1] # number of cells in the y direction
        nz = head['dims'][2] # number of cells in the z direction
        dx = head['dx'][0] # width of cell in x direction
        l_c = head['length_unit']
        t_c = head['time_unit']
        m_c = head['mass_unit']
        d_c = head['density_unit']                 
        v_c = head['velocity_unit']
        e_c = head['energy_unit']
        p_c = e_c # pressure units are the same as energy density units, density*velocity^2/length^3

        d  = f['d_xy'][:]
        px  = f['mx_xy'][:]
        py  = f['my_xy'][:]
        pz  = f['mz_xy'][:]
        E = f['E_xy'][:]

        f.close()

        if DE:
            GE = f['GE_xy'][:]

        mu = 1.0 # mean molecular weight (mu) of 1
        n = d * d_c/ (mu*mp) # number density, particles per cm^3  

        vx = px/d
        vy = py/d
        vz = pz/d
            
        if not DE:    
            KE = 0.5 * d * (vx*vx + vy*vy + vz*vz)
            GE = E - KE

        T = GE*(gamma-1.0)*p_c / (n*kb) #temperature
        logT = np.log10(T)

        # print('\t min \t\t\t max')
        # print('Vx: ', np.min(logT) , '\t' , np.max(logT))

        vmin = 3.9
        vmax = 6.2

        im = axs[j].imshow(logT.T, cmap='plasma', vmin=vmin, vmax = vmax) 
        axs[j].set_ylabel(labels[j], size=8, rotation='horizontal', ha='right', va='center', color=fig_color)
        axs[j].set_xticks(np.linspace(0,nx,9))
        axs[j].set_yticks(np.linspace(0,nz,5))
        axs[j].invert_yaxis()

        plt.setp(axs[j].spines.values(), color=fig_color)
        plt.setp([axs[j].get_xticklines(), axs[j].get_yticklines()], color=fig_color)

        if j == (len(sims)-1):
            axs[j].tick_params(axis='both', which='both', direction='in', color=fig_color, bottom=1, left=1, top=1, right=1, 
                    labelleft=0, labelbottom=1, labeltop=0, labelright=0, labelcolor=fig_color, labelsize=6)
            axs[j].set_xticklabels(np.round(np.arange(0,nx*dx+.01,0.2),1))
            [l.set_visible(False) for (i,l) in enumerate(axs[j].xaxis.get_ticklabels()) if i % 2 != 0]
            axs[j].set_xlabel('$kpc$', size=8, color=fig_color)
        else:
            axs[j].tick_params(axis='both', which='both', direction='in', color=fig_color, bottom=1, left=1, top=1, right=1, 
                    labelleft=0, labelbottom=0, labeltop=0, labelright=0)

    cb = fig.colorbar(im, ax=axs.ravel().tolist(), aspect=40, pad=0.025)
    cbar_yticks = plt.getp(cb.ax.axes, 'yticklabels')
    cb.ax.yaxis.set_tick_params(color=fig_color, labelsize=6)
    cb.outline.set_edgecolor(fig_color)
    plt.setp(cbar_yticks, color=fig_color)
    cb.ax.set_ylabel('$log_{10}(K)$', size=8, color=fig_color)

    fig.text(0.64, 0.9, str(int(t/t_cc))+r' $t_{cc}$', size=8, color=fig_color)

    plt.savefig(dnameout + str(i) + '.png', dpi=300, 
                bbox_inches='tight', pad_inches = 0.1, facecolor=bg_color) #facecolor=bg_color
    plt.close(fig)