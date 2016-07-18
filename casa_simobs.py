import os
import sys
import numpy as np
import scipy.constants as sc

'''

    Run in CASA with:
    >>> execfile('casa_simobs.py')

'''



def runSimobs(beamsizes, inttimes, files=None, mininttime=100.):

    '''
    beamsizes   :   float or list of floats. Beamsize in arcseconds.
    inttimes    :   float or list of floats. Integration time in minutes.
    files       :   None, string or list of strings. If strings, paths
                    to files to observe. If None, observe all .fits in
                    current folder.
    mininttime  :   integer. Minimum integration time.
    '''

    # Check type values.
    if type(beamsizes) is float:
        beamsizes = [beamsizes]
    elif type(beamsizes) is not list:
        raise TypeError('beamsizes must be a float or list of floats.')

    if type(inttimes) is float:
        inttimes = [inttimes]
    elif type(inttimes) is not list:
        raise TypeError('inttimes must be a float or list of floats.')

    if type(files) is str:
        files = [files]
    elif files is None:
        files = [d for d in os.listdir('./') if d.endswith('.fits')]
    elif type(files) is not list:
        raise TypeError('files must be None, a string or a list of strings.')

    
    # For each of the files, loop through simobserve process.
    for f, fn in enumerate(files):

        # Note that when we import a .fits into CASA the spectral axes are
        # converted automatically to frequency and all angular values are in
        # radians but need to be input in arcseconds.

        imname = '%s.image' % fn[:-5]
        importfits(fitsimage=fn, imagename=imname, overwrite=True)
        header = imhead(imname, mode='list')
        ia.open(imname)

        # For each permutation of integration time and beamsize, run simobserve()
        # and then simanalyze() to get workable images.

        for itime in inttimes:
            for bs in beamsizes:

                # Reset to default values and read in the sky model.
    
                default('simobserve')
                project = '%s' % (filein[:-5] + '_' + str(beamsize) 
                                  + 'arcsec_' + str(inttime) + 'mins')
                skymodel = '%s' % filein                        
                incenter = '%5.3fGHz' % (header['restfreq'] / 1e9)
                inwidth = '%5.3fMHz' % (header['cdelt3'] / 1e6)

                # If necessary, convert to 'Jy/pixel' from 'K'.

                if header['bunit'].lower() == 'jy/pixel':
                    jy2k = 1.
                else:
                    jy2k = 10**-26 * sc.c**2. / 2. / header['restfreq']**2.
                    jy2k /= sc.k * np.radians(header['cdelt2'])**2.

               inbright = '%5.3eJy/pixel' % (header['datamax']/jy2k)
               print 'Rescaling to peak flux of %s Jy/pix.' % inbright

                # The integration time is the number of 'data points' used for the 
                # simulated observation, hence CASA will essentially simulate
                # (totaltime / integration) of observations and combine. Typically
                # an integration time of 10s mimics real ALMA but makes it very, 
                # very slow.

                incell      = '%3farcsec' % (header['cdelt2'] * 206265.)
                integration = '%fs' % min(mininttime, inttime * 60)            
                totaltime   = '%f.0s' % (inttime * 60)
                antennalist = 'alma;%farcsec' % beamsize
                thermalnoise= 'tsys-atm'
                graphics    = 'file'

                # Run simobserve().

                simobserve()

                # Set up the cleaning. TODO: More options here.

                os.chdir(r'%s/' % project)
                default('clean')
                vis         = project +'.'+antennalist.replace(';','_') +'.noisy.ms'
                imagename   = 'CLEANed'

                # By default, clean all native channels.

                mode        = 'velocity'
                nchan       = -1
                start       = ''
                width       = ''

                # Set the level of appropriate cleaning.
                
                niter       = 10000
                threshold   = '0.1mJy'          
                restfreq    = '%fGHz'           % (header['restfreq'] / 1e9)
                interactive = False
                imsize      = 256               # 
                cell        = '%.5farcsec'      % (header['cdelt2'] * 206265. * 2.5)
                phasecenter = 0
                weighting   = 'briggs'
                robust      = 0.5
                pbcor       = False
                outframe    = 'LSRK'
                
                # Run clean(). 

                clean()

                # Clean up the files.

                os.system('rm *.txt')
                os.system('rm *.png')
                os.system('rm *.last')
                os.chdir(r'../')


                # Export as a .fits file.

                exportfits(imagename = project + r'/' + imagename + '.image',
                           fitsimage = (filein[:-5] + '_' + str(beamsize) + 
                                        'arcsec_' + str(inttime) + 'mins_simobs.fits'),
                           overwrite = True,
                           dropstokes= True,
                           velocity  = True)

    return




for f, filein in enumerate(files):

    #--IMPORT FITS -----------------------------------------------------------------

    # Load the fits file.
    # Note that velocity axes are automatically changed to frequency.
    # The angular sizes are converted to radians but needs to be input as arcsec.


    # Loop through each permutation of the build.
    for inttime in inttimes:
        for beamsize in beamsizes:

            #-- SIMOBSERVE ---------------------------------------------------------




            #-- SIMANALYZE ---------------------------------------------------------

            # Set up the CLEAN parameters. Change as necessary.


            
            
    #-------------------------------------------------------------------------------

    # Clean up files.
    os.system(r'rm *.last')
    #os.system(r'mv *.fits ../')
    #os.chdir(r'../')
    #os.system(r'rm *.log')

    
    if not os.path.isdir(filein[:-5]+'_Outputs'): os.mkdir(filein[:-5]+'_Outputs')
    os.system(r'mv %s*.fits ./%s_Outputs/' % (filein[:-5], filein[:-5]))

    if not os.path.isdir('SimObs_'+filein[:-5]): os.mkdir('SimObs_'+filein[:-5])
    os.system(r'mv %s* ./SimObs_%s/' % (filein[:-5], filein[:-5]))

    print 'Completed: %d / %d.' % (f+1, len(files))



