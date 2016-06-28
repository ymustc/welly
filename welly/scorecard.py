# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Makes display of a well's contents (scorecard)
:copyright: 2016 Agile Geoscience
:license: Apache 2.0
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from .well import Well, WellError
from welly import Well, Curve
from striplog import Striplog, Legend, Component

track_titles = ['MD',
                'Lithology',
                'Resistivity',
                'Porosity',
                'Density',
                'Sonic',
                'Canstrat']

curve_layout = {'C1': 0, 'CALS': 0, 'CAX': 0, 'CAY': 0, 'CALI': 0,
                'GR': 1, 'GAM': 1,
                'PEF': 1, 'SP': 1,
                'ILD': 2, 'ILM': 2, 'SFL': 2, 'CILD': 2, 'NOR': 2, 'MFR': 2,
                'LL8': 2, 'LLD': 2, 'LLS': 2, 'INV': 2,
                'NPSS': 3, 'PDS': 3, 'NPLS': 3, 'DPSS': 3, 'DPLS': 3,
                'POS': 3, 'POL': 3,
                'RHOB': 4, 'DEN': 4, 'DRHO': 4, 'DC': 4, 'DTLN': 4,
                'DT': 5, 'DT4P': 5, 'AC': 5, 'ACL': 5}


class Scorecard(Well):
    """
    Creates a scorecard representation of a well.
    """

    def __init__(self, params):
        """
        Generic initializer for now.
        """
        for k, v in params.items():
            if k and v:
                setattr(self, k, v)

        if getattr(self, 'data', None) is None:
            self.data = {}

    def scorecard_fig(self, figheight=6, figwidth=8):
	    """
	    makes a well scorecard figure from contents of a well object
	    param: vscale: vertical scale in metres per inch
	    """
	    fig = plt.figure(figsize=(figwidth, figheight)) 
	    gs = gridspec.GridSpec(1, 6, width_ratios=[3,3,3,3,3,1]) 
	    ax1 = plt.subplot(gs[0])
	    ax2 = plt.subplot(gs[1])
	    ax3 = plt.subplot(gs[2])
	    ax4 = plt.subplot(gs[3])
	    ax5 = plt.subplot(gs[4])
	    ax6 = plt.subplot(gs[5])
	    axarr = [ax1, ax2, ax3, ax4, ax5, ax6]
	    return fig, axarr
	
    def plot_bars(self, axarr, fs=8, start=0, buff=0.2):
	    """
	    plots various bars in tracks
	    """
	    trackplace = np.zeros(len(axarr))
	    basis = self.data['DEPT'] or self.data['DEPTH']
	    for curve in self.data.keys():
	        if curve != 'DEPT' or 'DEPTH' and type(self.data[curve]) == type(basis):
	            top, base, height = get_bar_range(self.data[curve])
	            name, units, descr = get_curve_text(self.data[curve])
	            color = get_curve_color(units)
	            track = track_dict[curve]  # which axes
	            if color == 'green':  # first track
	                p = 0
	            if color == 'magenta':  # second track
	                p = 1
	            if color == 'red':  # third track
	                p = 2
	            if color == 'blue':  # fourth track
	                p = 3
	            if color == 'navy':  # fifth track
	                p = 4
	            if color == 'grey':  # sixth track
	                p = 5
	            ax = axarr[p]
	            # Plot the bar
	            for t, b, h in zip(top, base, height):
	                ax.bar(start + trackplace[p] + buff, h, bottom=self.data[curve].basis[t],
	                       width=0.8, alpha=0.2, color=color)
	                # Plot the name in the middle
	                ax.text(start + trackplace[p] + 0.5 + buff, 0 + 350, name,
	                        fontsize=fs, ha='center', va='top', rotation='vertical')
	                # Plot curve units
	                ax.text(start + trackplace[p] + 0.5 + buff, 0 + 50, units,
	                        fontsize=fs, ha='center', va='top', rotation='vertical')
	            trackplace[p] += 1
	    [ax.set_xlim(-1, max(trackplace)+1) for ax in axarr]
	    return axarr

    def get_bar_range(curve):
	    '''
	    Returns the depth of the bottom of the log (and the height) for bar chart
	    '''
	    tops = []    # top of log
	    bots = []    # bottom of log
	    # find index of first real value of curve
	    index = np.where(np.isfinite(np.array(curve)))[0]
	    tops.append(index[0])
	    # find bottom of log or missing points
	    for i in np.arange(index.size - 1):
	        if (index[i + 1] - index[i]) > 1:
	            bots.append(index[i])
	            # print ('null value here: ', i, ' index', index[i])
	            tops.append(index[i + 1])
	    bots.append(index[-1])
	    top = np.asarray(tops)
	    base = np.asarray(bots)
	    height = curve.basis[base] - curve.basis[top]
	    return top, base, height


    def get_curve_text(curve):
	    name = curve.mnemonic
	    units = curve.units
	    descr = curve.description
	    return name, units, descr

    
    def get_curve_color(units):
	    """
        Returns the colour for the bar based on the curve units
        """
	    colorcurves = {
	    			   'GAPI': 'green', 'API': 'green','NAPI': 'green', 'B/E': 'green',
	                   'OHMM': 'magenta', 'OHM.M': 'magenta', 'OHM/M': 'magenta', 
	                   'MMHO/M': 'magenta',
	                   'V/V': 'red', 'PU': 'red', '%': 'red', 'M3/M3': 'red',
	                   'DEC': 'red',
	                   'K/M3': 'blue', 'G/C3': 'blue', 'KG/M3': 'blue',
	                   'KGM3': 'blue',
	                   'G/C3': 'blue', 'G/CM3': 'blue',
	                   'US/M': 'navy', 'USEC/M': 'navy', 'US/F': 'navy',
	                   'US/FT': 'navy',
	                   'MV': 'green',
	                   'MM': 'green'
	                   }

	    if units.upper() in colorcurves:
	        color = colorcurves[units.upper()]
	    else:
	        color = 'grey'
	    return color

    
    def put_track_names(axarr, fs=10):
        """
        Puts label of track type in each track
    	"""
        for ax, text in zip(axarr[:-1], track_titles[1:-1]):
	        ax.text(x=0.5, y=0.0, s=text, fontsize=14,
	                ha='center', va='bottom', transform=ax.transAxes)
        return 


    def plot_striplog(axarr, striplog):
        """
		Plot stiplog (if the well has one)
        """
        if striplog is not None:
            axarr[-1] = striplog.plot(ax=axarr[-1], aspect=0.2, 
	                                  legend=legend, match_only=['lithology'])
            axarr[-1].set_title('Canstrat \n Lithology')
            axarr[-1].set_ylim([get_td(well), 0])
            axarr[-1].set_yticklabels([])
            axarr[-1].spines['right'].set_visible(True)
            axarr[-1].spines['top'].set_visible(True)
            axarr[-1].spines['bottom'].set_visible(True)
        return 


    def put_tops(axarr, topsdata):
        """
		Put tops across all tracks
        """
        if topsdata is not None:
            for i, ax in enumerate(axarr):
                ax.set_ylim([get_td(well), 0])
                ax.set_xticks([])
                if i > 0:
                   ax.set_yticks([])
	            
                for pick in well.data[topsdata]:
                    name = pick.primary.formation
                    depth = pick.top.middle
                    ax.axhline(depth, lw=2, color='k', xmax=1.05,
                               path_effects=[path_effects.SimpleLineShadow(),
                               path_effects.Normal()])
                    if i == len(axarr)-1:
                        ax.text(x=ax.get_xlim()[-1]*1.0*1.1, y=depth, s=name, 
                                ha='left', va='center')
        return 


    def put_side_text(axarr):
	    # label kb elevation   
        axarr[-1].text(x=1.4, y=1.0, s='KB elev.:'+str(well.location.kb)+' m', 
	                   fontsize=8, ha='left', va ='top', transform=ax.transAxes)
	    # label td elevation (measured depth)
        axarr[-1].text(x=1.4, y=0.0, s='TD:'+str(round(well.location.td))+' m', 
	                   fontsize=8, ha='left', va ='bottom', transform=ax.transAxes)
        return 


    def put_header_text(fig):
        fig.text(x=0.05, y=0.925, s= well.header.name, fontsize=14)
        fig.text(x=0.05, y=0.910, s= 'UWI: '+well.header.uwi, fontsize=12)
        fig.subplots_adjust(wspace=0, hspace=0)
        return fig


    def adjust_fig_dims(fig):
        fig.set_figheight(get_td(well)/vscale)
        fig.set_figwidth(width)
        return fig

    def scorecard(self, striplog, topsdata):
        fig, axarr = scorecard_fig(self)
        axarr = plot_bars(axarr)
        put_track_names(axarr)
        put_striplog(axarr)
        put_tops(axarr)
        put_side_text(axarr)
        put_header_text(fig)
        adjust_fig_dims(fig)
        return fig