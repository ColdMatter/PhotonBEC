"""Object-oriented, high-level interface for Andor cameras (SDK2), written in Cython. 

.. Note::
   
   - This is not a stand-alone driver. Andor's proprietary drivers must be installed.
     The setup script expects to find ``libandor.so`` in ``/usr/local/lib/``
     (the driver's default installation directory).
   
   - Andor provides a low-level, :mod:`ctypes` wrapper on their SDK, called ``atcmd``.
     If available, it will be imported as :attr:`Andor._sdk`.
     
   - This documentation should be read along Andor's Software Development Kit manual.
   
   - **To build the extension**::
   
     $ python2.7 setup_extension.py build_ext --inplace

.. Warning::
   This module is not thread-safe. If :func:`AcqMode.wait` is blocking a
   background thread, and another function call is made from the main thread,
   the main thread will block too.

-----------------------------

:Usage:

The camera is controlled via the top-level class :class:`Andor`:

>>> from andor2 import Andor
>>> cam = Andor()

The :class:`Andor` instance is just a container for other objects
that control various aspect of the camera:

* :class:`Info` : camera information and available features
* :class:`Temperature` : cooler control
* :class:`Shutter` : shutter control
* :class:`EM`: electron-multiplying gain control
* :class:`Detector`: CCD control, including:

  - :class:`VSS`: vertical shift speed
  - :class:`HSS`: horizontal shift speed
  - :class:`ADC`: analog-to-digital converter
  - :class:`OutputAmp`: the output amplifier
  - :class:`PreAmp`: pre-amplifier control

* :class:`ReadMode`: select the CCD read-out mode (full frame, vertical binning, tracks, etc.)
* :class:`Acquire <AcqMode>`: control the acquisition mode (single shot, video, accumulate, kinetic)

:Examples:

>>> from andor2 import Andor
>>> cam = Andor()
>>> cam.Temperature.setpoint = -74  # start cooling
>>> cam.Temperature.cooler = True  
>>> cam.Detector.OutputAmp(1)       # use conventional CCD amplifier instead of electron multiplying
>>> cam.PreAmp(2)                   # set pre-amplifier gain to 4.9
>>> cam.exposure = 10               # set exposure time to 10 ms
>>> cam.ReadMode.SingleTrack(590,5) # set readout mode: single track, 5 pixels wide, centered at 590 pixels

>>> cam.Acquire.Video()             # set acquisition mode to video (continuous)
>>> data = cam.Acquire.Newest(10)   # collect latest 10 images as numpy array
>>> cam.Acquire.stop()

>>> cam.Acquire.Kinetic(10, 0.1, 5, 0.01)    # set up kinetic sequence of 10 images every 100ms
                                             # with each image being an accumulation of 5 images
                                             # taken 10ms apart
>>> cam.Acquire.start()                      # start acquiring
>>> cam.Acquire.wait()                       # block until acquisition terminates
>>> data = cam.Acquire.GetAcquiredData()     # collect all data

-----------

"""

# When compile, we get a 'warning: #warning "Using deprecated NumPy API"'
# This is a Cython issue, see https://mail.python.org/pipermail/cython-devel/2014-June/004048.html
 
import numpy as np
cimport numpy as np
np.import_array()

import time
import h5py

cimport cython
cimport atmcdLXd as sdk   # Andor SDK definition file

# Try importing Andor's own python wrapper
try:
  import atmcd
  WITH_ATMCD = True
except ImportError:
  WITH_ATMCD = False

# Errors
class AndorError(Exception):
  def __init__(self, error_code, sdk_func = None):
    self.code = error_code
    self.string = ERROR_CODE[self.code]
    self.sdk_func = sdk_func
  def __str__(self):
    return self.string

def andorError(error_code, ignore = (), info = ()):
  """andorError(error_code, ignore = (), info = ())
  
  Wrap each SDK function in andorError to catch errors.
  Error codes in 'ignore' will be silently ignored, 
  while those is 'info' will trigger and AndorInfo exception. ??? not for now, not sure what to do with those...
  for now they will just print the error message"""
  if (error_code in info):
    print("Andor info: " + ERROR_CODE[error_code])
  elif (error_code != sdk.DRV_SUCCESS) and (ERROR_CODE[error_code] not in ignore):
    raise AndorError(error_code)
  else:
    pass
  
def _initialize(library_path = "/usr/local/etc/andor/"):
  andorError(sdk.Initialize(library_path))
  
def _shutdown():
  andorError(sdk.ShutDown())
    
def AvailableCameras():
  """Return the total number of Andor cameras currently installed.
  
  It is possible to call this function before any of the cameras are initialized.
  """
  cdef np.int32_t totalCameras
  andorError(sdk.GetAvailableCameras(&totalCameras))
  return totalCameras
  
def while_acquiring(func):
  """Decorator that allows calling SDK functions while the camera is
  acquiring in Video mode (acquisition will stopped and restarted).
  """
  def decorated_function(*args, **kwargs):
    self = args[0]
    try:
      func(*args, **kwargs)
    except AndorError as error:
      if error.string is "DRV_ACQUIRING" and self._cam.Acquire._name is 'Video':
        andorError(sdk.AbortAcquisition())
        func(*args, **kwargs)
        andorError(sdk.StartAcquisition())
      else:
        raise error
  return decorated_function
  
def rollover(func):
  """ Decorator that correct for the ADC roll-over by replacing zeros
  with 2**n-1 in image data.
  """
  def inner(*args, **kwargs):
    self = args[0]
    data = func(*args, **kwargs)
    if self.rollover:
      dynamic_range = 2**self._cam.Detector.bit_depth - 1
      data[data==0] = dynamic_range
    return data
  return inner
  
class Andor(object):
  """High-level, object-oriented interface for Andor cameras (SDK v2).
  
  :Usage: 
   
  The UI contains the following objects, most of which are self-explanatory:
  
  - :class:`Info` : camera information and available features
  - :class:`Temperature` : cooler control
  - :class:`Shutter` : shutter control
  - :class:`EM`: electron-multiplying gain control
  - :class:`Detector`: CCD control, including:
  
    - :class:`VSS`: vertical shift speed
    - :class:`HSS`: horizontal shift speed
    - :class:`ADC`: analog-to-digital converter
    - :class:`OutputAmp`: the output amplifier
    - :class:`PreAmp`: pre-amplifier control
    
  - :class:`ReadMode`: select the CCD read-out mode (full frame, vertical binning, tracks, etc.)
  - :class:`Acquire <AcqMode>`: control the acquisition mode (single shot, video, accumulate, kinetic)
    
  Upon initialisation, the camera is set by default to:
    - Acquisition mode: single shot
    - Readout mode: full image
    - EM gain: off
    - Vertical shift speed: maximum recommanded
    - Horizontal shift speed: second fastest.
  """
  
  def __init__(self, init=True, lib="/usr/local/etc/andor/"):
    """Initialize the camera and returns a user-friendly interface. 
    
    :param bool init:  set to False to skip the camera initialisation
                       (if it has been initialised already).
    :param lib: location of the Andor library.
    """
    if init:
      andorError(sdk.Initialize(lib))
    self._cam = self
    self.Info = Info()
    self.Temperature = Temperature(self)
    self.Shutter = Shutter(self)
    self.EM = EM(self)
    #self.PreAmp = PreAmp(self) # moved to Detector
    self.Detector = Detector()
    self.ReadMode = ReadModes(self.Info.capabilities._ReadModes, {"_cam": self})
    self._AcqMode = AcqModes(self.Info.capabilities._AcqModes, {"_cam": self})
    # Set up default modes: Single Acq, Image
    self.ReadMode.Image()
    self.Acquire = self._AcqMode.Video
    self.Acquire(start=False)
    # Make Andor's ctypes wrapper accessible, if available
    if WITH_ATMCD:
      self._sdk = atmcd.atmcd()
    
  def __del__(self):
    self.Acquire.stop()
    self.Shutter.Close()
    andorError(sdk.ShutDown())
  
  @property
  def exposure(self):
    """Query or set the exposure time, in ms."""
    t = self.acquisitionTimings
    return t['exposure'] * 1000.0
  @exposure.setter
  @while_acquiring
  def exposure(self, value):
      andorError(sdk.SetExposureTime(value/1000.0))

  @property 
  def acquisitionTimings(self):
    """Returns the actual exposure, accumulation and kinetic cycle times, in seconds."""
    cdef float exp, acc, kin
    andorError(sdk.GetAcquisitionTimings(&exp, &acc, &kin))
    return {'exposure': exp, 'accumulate': acc, 'kinetic': kin}

class Info(object):
  """Information about the camera.
  
  Includes:
     - serial number
     - controller card model
     - capabilities (see :class:`Capabilities` for details)
  """
  def __init__(self):
    cdef int serial
    andorError(sdk.GetCameraSerialNumber(&serial))
    self.serial_number = serial
    cdef char *controllerCardModel
    controllerCardModel = "          "
    andorError(sdk.GetControllerCardModel(controllerCardModel))
    cdef char[256] head
    andorError(sdk.GetHeadModel(&head[0]))
    self.head_model = head
    self.controller_card = controllerCardModel
    self.capabilities = Capabilities()
    #... more to come
    
  def __repr__(self):
    return "<Andor %s %s camera, serial number: %d>" % (self.capabilities.CameraType, self.head_model, self.serial_number)

class OutputAmp(object):
  """The output amplifier.
  
  Some cameras have a conventional CCD amplifier in addition to the EMCCD amplifier, 
  although often the EMCCD amplifier is used even with the gain switched off, 
  as it is faster.
  """
  def __init__(self):
    self._active = 0
    self.__call__(0)
  
  def __repr__(self):
    return "<Currently active amplifier: " + self.description()+ ". Number of available amplifiers: "+ str(self.number)+'>'
  
  @property
  def number(self):
    """Returns the number of available amplifier."""
    cdef int noAmp
    andorError(sdk.GetNumberAmp(&noAmp))
    return noAmp

  @property
  def max_speed(self):
    """ Maximum available horizontal shift speed for the amplifier currently selected."""
    cdef float speed
    andorError(sdk.GetAmpMaxSpeed(self._active, &speed))
    return speed
  
  def __call__(self, amp):
    """Set the output amplifier
    0: Standard EMCCD (default)
    1: Conventional CCD (if available)
    """
    andorError(sdk.SetOutputAmplifier(amp))
    self._active = amp
    
  @property
  def active(self):
    """Return the index of the current output amplifier."""
    return self._active

  def description(self, index=None):
    """ Return a string with the description of the currently selected amplifier.
    
    Options:
    - index: select a different amplifier
    """
    cdef char *name
    name = "                     " # init char with length 21
    if index == None: 
      index = self._active
    andorError(sdk.GetAmpDesc(index, name, 21))
    return name    


class HSS(object):
  """Controls the horizontal shift speed.  
  
  The HSS depends on the *output amplifier* (which must be passed to the constructor)
  and on the analog-to-digital converters (which is created within the HSS object).
  
  :Usage:
  
  >>> print hss.speeds  # query available settings
  >>> hss(0)            # set speed to hss.speeds[0]
  
  """
  # might be a good idea to not call the SDK functions every time...
  def __init__(self, OutAmp):
    """:param OutAmp: :class:`OutputAmp` instance."""
    self.ADC = ADC(self)
    self.OutputAmp = OutAmp
    self.__call__(0) # default to second fastest speed.
    self.choose = self.__call__
    self.list_settings = []
    self.current = None
    self.ADC.ADConverters = self.ADC.list_ADConverters()
    
  @property 
  def info(self):
    return self.__repr__()
 
  @property
  def number(self):
    """Return the number of HS speeds available."""
    cdef int noHSSpeed
    andorError(sdk.GetNumberHSSpeeds(self.ADC.channel, self.OutputAmp.active, &noHSSpeed))
    return noHSSpeed
  
  @property
  def speeds(self):
    """Return a dictionary of available speeds {index: speed (MHz),... }."""
    cdef float speed
    HSSpeeds = {}
    for index in range(self.number):
      andorError(sdk.GetHSSpeed(self.ADC.channel, self.OutputAmp.active, index, &speed))
      HSSpeeds[index] = speed
    return HSSpeeds
      
  def __repr__(self):
    return "<Horizontal shift speed value: %fMHz. Possible values: %s>" % (self.current, self.speeds)
      
  def __call__(self, index=None):
    """Set the speed to that given by the index, or let the user choose from menu."""
    if index is None:
      print("Select horizontal shift speed values from: ")
      print(self.speeds)
      choice = input('> ')
    else:
      choice = index
    andorError(sdk.SetHSSpeed(self.OutputAmp.active, choice))
    self.current = self.speeds[choice]


class VSS(object):
  """Controls the vertical shift speed (VSS).
  
  Upon initialisation, it defaults to the fastest recommanded speed.
  Call the class with no arguments to select a different speed.
  
  :Usage:
  
  >>> vss.speeds      # Available settings
  >>> vss(7)          # Set speed to no 7 (fastest)
  >>> vss.voltage = 4 # Increase clock voltage to redude CIC noise at high speed.
  
  """
  def __init__(self):
    cdef int noVSSpeed
    andorError(sdk.GetNumberVSSpeeds(&noVSSpeed))
    #: Number of available settings
    self.number = noVSSpeed
    #: Available settings
    self.speeds = {}
    cdef float speed
    for index in range(noVSSpeed):
      andorError(sdk.GetVSSpeed(index, &speed))
      self.speeds[index] = speed
    self._fastestRecommended = self.fastestRecommended
    self.__call__(index=self._fastestRecommended["index"])
    self.choose = self.__call__
    self._voltage = 0
      
  def __repr__(self):
    return "<Current vertical shift speed: "+ str(self.current) + "us. \nPossible values : " + str(self.speeds) + "\nMax Recommanded: "+str(self.fastestRecommended)+'>'
    
  @property 
  def info(self):
    return self.__repr__()
    
  def __call__(self, index=None):
    """Set the speed to that given by the *index*, or choose from a menu."""
    if index is None:
      print("Select vertical shift speed values (in us) from: ")
      print(self.speeds)
      choice = input('> ')
    else:
      choice = index
    andorError(sdk.SetVSSpeed(choice))
    self.current = self.speeds[choice]
  
  @property
  def fastestRecommended(self):
    """Query the fastest recommended speed (in us)."""
    cdef int index
    cdef float speed
    andorError(sdk.GetFastestRecommendedVSSpeed (&index, &speed))
    return {"index": index, "speed": speed}
  
  @property
  def voltage(self):
    """Set or query the vertical clock voltage.
    
    If you choose a high readout speed (a low readout time), then you should also consider
    increasing the amplitude of the Vertical Clock Voltage.
    There are five levels of amplitude available for you to choose from:
    Normal (0); +1, +2, +3, +4.
    Exercise caution when increasing the amplitude of the vertical clock voltage, since higher
    clocking voltages may result in increased clock-induced charge (noise) in your signal. In
    general, only the very highest vertical clocking speeds are likely to benefit from an
    increased vertical clock voltage amplitude.
    """
    return self._voltage
  
  @voltage.setter
  def voltage(self, v):
    andorError(sdk.SetVSAmplitude(v))
    self._voltage = v
   
         
class ADC(object):
  """The analog-to-digital converter.
  
  Some cameras have more than one ADC with a different dynamic range (e.g. 14 and 16 bits). 
  The choice of ADC will affect the allowed horizontal shift speeds: see the ADConverters
  property for a list of valid comninations.
  
  :Usage:
  
  >>> adc.bit_depth   # dynamic range with current setting
  >>> adc.channel     # currently selected ADC
  >>> adc.channel = 1 # select other ADC
  """
  def __init__(self, HSS=None):
    self.HSS = HSS
    self.channel = 1
    # Don't finalise initialisation here as HSS.__init__() may not have completed yet!
  
  def list_ADConverters(self):
    adc = []
    current_channel = self.channel
    for i in range(self.number):
      self.channel = i
      if self.HSS is None:
        adc.append({"index": i, "bit_depth": self.bit_depth})
      else:
        adc.append({"index": i, "bit_depth": self.bit_depth, "HSSpeeds": self.HSS.speeds})
    self.channel = current_channel
    return adc
      
  @property
  def number(self):
    """Returns the number of analog-to-digital converters."""
    cdef int chans
    andorError(sdk.GetNumberADChannels(&chans))
    return chans    
  
  @property
  def channel(self):
    """Set or query the currently selected AD converter."""
    return self._channel
  @channel.setter
  def channel(self, chan):
    andorError(sdk.SetADChannel(chan))
    self._channel = chan
    
  @property
  def bit_depth(self):
    """Returns the dynamic range of the currently selected AD converter."""
    cdef int depth
    andorError(sdk.GetBitDepth(self._channel, &depth))
    return depth
    
  def __repr__(self):
    return "Currently selected A/D converter: "+ str(self.channel) +" ("+str(self.bit_depth) + " bits).\nPossible settings are: " + str(self.ADConverters)

class EM(object):
  """ Controls the electron multiplying gain.
  
  :Usage:
  
  >>> EMGain.on()       # Turn EM gain on 
  >>> EMGain.gain = 123 # Set gain
  >>> EMGain.off()       # Turn EM gain off
  
  **Note:** setting the gain to 0 is the same as switching it off.
  """
  def __init__(self, cam):
    self._cam = cam
    current = self._read_gain_from_camera(readonly=False) # read current setting and set software parameters
    self.modes = {"default": 0, "extended": 1, "linear": 2, "real": 3}
    self._mode = self.modes["default"]
  
  @property
  def range(self):
    """Query the range of valid EM gains."""
    cdef int low, high
    andorError(sdk.GetEMGainRange(&low, &high))
    return (low, high)

  def _read_gain_from_camera(self, readonly = True):
    cdef int value
    andorError(sdk.GetEMCCDGain(&value))
    if not readonly: 
      # reset software value of sensor gain
      andorError(sdk.GetEMCCDGain(&value))
      self._switch = (value > 0)
      self._gain = value
    return value
    
  @property
  def gain(self):
    """Set or query the current setting."""
    return self._gain
  @gain.setter
  @while_acquiring
  def gain(self, value):
    self._gain = value
    # only update the sensor gain if EM gain is ON:
    if self._switch:
      andorError(sdk.SetEMCCDGain(value))
  
  def __call__(self, gain=None):
    """Set or query the current setting."""
    if gain is None:
      return self.gain
    else:
      self.gain = gain
  
  @while_acquiring  
  def on(self):
    """Turn on the EM gain."""
    andorError(sdk.SetEMCCDGain(self._gain))
    self._switch = True
  
  @while_acquiring  
  def off(self):
    """Turn off the EM gain."""
    andorError(sdk.SetEMCCDGain(0))
    self._switch = False
    
  @property
  def is_on(self):
    """Query whether the EM gain is on."""
    return self._switch
  @is_on.setter
  def is_on(self, state):
    if state:
      self.on()
    else:
      self.off()
    
  def __repr__(self):
    if self._switch:
      return "EMCCD gain is ON, gain value: " + str(self.gain) + "."
    else:
      return "EMCCD gain is OFF."
  
  @property
  def status(self):
    return self.__repr__()
    
  @property
  def advanced(self):
    """Turns on and off access to higher EM gain levels.
    
    Typically optimal signal to noise ratio and dynamic range is achieved between x1 to x300 EM Gain.
    Higher gains of > x300 are recommended for single photon counting only. Before using
    higher levels, you should ensure that light levels do not exceed the regime of tens of
    photons per pixel, otherwise accelerated ageing of the sensor can occur.
    """
    return self._advanced
  @advanced.setter
  def advanced(self, bint state):
    andorError(sdk.SetEMAdvanced(state))
    self._advanced = state
    
  @property
  def mode(self):
    """The EM Gain mode can be one of the following possible settings:
    
    - 0: The EM Gain is controlled by DAC settings in the range 0-255. Default mode.
    - 1: The EM Gain is controlled by DAC settings in the range 0-4095.
    - 2: Linear mode.
    - 3: Real EM gain
    
    To access higher gain values (if available) it is necessary to enable advanced EM gain,
    see SetEMAdvanced.
    """
    return self._mode
  @mode.setter
  def mode(self, mode):
    if isinstance(mode, str):
      value = self.modes[mode]
    else:
      value = mode
    andorError(sdk.SetEMGainMode(mode))
    self._mode
    
class Temperature(object):
  """Manages the camera cooler. 
  
  Default temperature setpoint is -65C.
  """
  def __init__(self, cam):
    self._cam = cam
    self._setpoint = -65
    
  @property
  def range(self):
    """Return the valid range of temperatures in centigrade to which the detector can be cooled."""
    cdef int tmin, tmax
    andorError(sdk.GetTemperatureRange(&tmin, &tmax))
    return (tmin, tmax)
  
  @property
  def precision(self):
    """Return the number of decimal places to which the sensor temperature can be returned.""" 
    cdef int precision
    andorError(sdk.GetTemperaturePrecision(&precision))#, ignore = (sdk.DRV_NOT_SUPPORTED,))
    return precision
    
  @property
  def setpoint(self):
    """Return the current setpoint."""
    return self._setpoint
  
  @setpoint.setter
  def setpoint(self, value):
    """Change the setpoint."""
    andorError(sdk.SetTemperature(value))
    self._setpoint = value
    
  @property
  def read(self):
    """Returns the temperature of the detector to the nearest degree, and the status of cooling process."""
    cdef int value
    error_code = sdk.GetTemperature(&value)
    andorError(error_code, ignore={ERROR_CODE[k] for k in TEMPERATURE_MESSAGES})
    return {"temperature": value, "status": ERROR_CODE[error_code]}

  @property
  def cooler(self):
    """Query or set the state of the TEC cooler (True: ON, False: OFF)."""
    cdef bint state
    andorError(sdk.IsCoolerOn(&state)) # returns 1 if on, 0 if off
    return state
  @cooler.setter  
  def cooler(self, state):
    if state:
      andorError(sdk.CoolerON())
    else:
      andorError(sdk.CoolerOFF())
      
  def __repr__(self):
    return "Current temperature: " + str(self.read) + ", cooler: "+ ("ON" if str(self.cooler) else "OFF") + ", setpoint: " + str(self.setpoint)+"." 
  
class PreAmp(object):
  """The pre-amplifier gain.
  
  Callable.
  
  :Usage:
  
  >>> preamp.gain # current setting
  >>> preamp()    # choose the gain from a menu
  """
  def __init__(self):
    #self._cam = cam
    #: Number of PreAmp settings available.
    self.number = self._number()
    self.gains = self.list_gains()
    self.__call__(1)
    self.choose = self.__call__
  
  def _number(self):
    """Number of PreAmp settings available."""
    cdef int noGains
    andorError(sdk.GetNumberPreAmpGains(&noGains))
    return noGains
  
  def list_gains(self):
    """Return a dictionary {index: gain, ...} of the available settings."""
    cdef float gain
    gain_list = {}
    for index in range(self.number):
      andorError(sdk.GetPreAmpGain(index, &gain))
      gain_list[index] = gain
    return gain_list
  
  @while_acquiring
  def __call__(self, index=None):
    """Set the PreAmp gain. If no index is given, choose from a menu."""
    if index == None:
      print("Select PreAmp gain from: ")
      print(self.gains)
      choice = input('> ')
    else:
      choice = index
    andorError(sdk.SetPreAmpGain(choice))
    self._gain = {"index": choice, "value": self.gains[choice]}
    
  @property
  def gain(self):
    """Current pre-amplifier gain."""
    return self._gain["value"]
    
  def __repr__(self):
    return "Current PreAmp gain: x" + str(self.gain) + ". Possible settings: " + str(self.gains)


class Shutter(object):
  """Controls the internal shutter.
  
  Use Open(), Closed() or Auto(), or Set(TTL, mode. closingtime openingtime) for custom operation.
  The opening/closing times ar set to minimum by default.
  """
  def __init__(self, cam):
    self._cam = cam
    cdef bint isInstalled
    andorError(sdk.IsInternalMechanicalShutter(&isInstalled))
    self.installed = isInstalled
    self.transfer_times = self.MinTransferTimes
    self.mode = {"auto":0, "open": 1, "closed": 2, "open for FVB series": 4, "open for any series": 5}
    self.TTL_open = {"low":0, "high": 1}
    self.state = None
  
  @property 
  def MinTransferTimes(self):
   cdef int minclosingtime, minopeningtime
   andorError(sdk.GetShutterMinTimes(&minclosingtime,&minopeningtime))
   return {"closing": minclosingtime, "opening": minopeningtime}
  
  def Set(self, mode, ttl=None, closingtime=None, openingtime=None):
    if ttl is None: ttl = self.TTL_open["high"]
    if closingtime is None: closingtime = self.transfer_times["closing"]
    if openingtime is None: openingtime = self.transfer_times["opening"]
    andorError(sdk.SetShutter(ttl, mode, closingtime, openingtime))
  
  @while_acquiring
  def Open(self):
    self.Set(self.mode["open"])
    self.state = "open"
  
  @while_acquiring
  def Close(self):
    self.Set(self.mode["closed"])
    self.state = "closed"
    
  def Auto(self):
    self.Set(self.mode["auto"])
    self.state = "auto"
    
  def __repr__(self):
    return "Internal Shutter present and currently + self.state." if self.installed else "No internal shutter."

class Detector(object):
  """Represents the EMCCD sensor.
  
  In addition to providing properties to access the pixel size (in um),
  sensor dimensions (in pixels), and bit depth, this class is also a container for:
  
    - the horizontal shift speed
    - the vertical shift speed
    - the output amplifier
    - the preamplifier
    - the A/D converter
  """
  # NOTE: actually the AD converter and output amp are not really part of the sensor, if we limit it to the 2D CCD array...
  def __init__(self):
    self.VSS = VSS()
    self.OutputAmp = OutputAmp()
    self.HSS = HSS(self.OutputAmp)
    self.ADC = self.HSS.ADC
    self.PreAmp = PreAmp() 
    self.size = self._size
    #: 
    self.pixel_size = self._pixel_size
  
  @property
  def _pixel_size(self):
    """Returns the dimension of the pixels in the detector in microns."""
    cdef float xSize, ySize
    andorError(sdk.GetPixelSize(&xSize, &ySize))
    return (xSize, ySize)
    
  @property
  def _size(self):
    """Returns the size of the detector in pixels. The horizontal axis is taken to be the axis parallel to the readout register."""
    cdef int xpixels, ypixels
    andorError(sdk.GetDetector(&xpixels, &ypixels))
    self.width = xpixels
    self.height = ypixels
    self.pixels = xpixels * ypixels
    return (xpixels, ypixels)
  
  @property
  def bit_depth(self):
    return self.ADC.bit_depth
    
  def __repr__(self):
    return "Andor CCD | "+str(self.size[0])+"x"+str(self.size[1]) +" pixels | Pixel size: " + str(self.pixel_size[0])+"x"+str(self.pixel_size[1]) +"um."


# CAPABILITIES
# Upon initialisation, the camera capabilities are determined and only the valid ones 
# are made available.

class _AddCapabilities(object):
  """Populates a type of capabilities (ReadModes, AcqModes etc.) with only the modes that are available.
  
  :Usage:
  
  >>> self._capabilities = _Capabilities()
  >>> self.ReadMode = _AddCapabilities(self._capabilities._ReadModes, ref)
  >>> self.AcqMode = _AddCapabilities(self._capabilities._AcqModes)
  
  *ref* is a dict of {"string": object} tuple giving an optional object to insert as attribute 'string'
  """
  def __init__(self, caps, ref = {}):
    for c in caps:
      if c._available:
        setattr(c, c._typ, self) # include reference to higher-level class of the right type.
        for key, value in ref.iteritems(): # add custom references
          setattr(c, key, value)
        setattr(self, c._name, c) # create Capability with the right name
    self.current = None
    
  @property 
  def info(self):
    """ Print user-friendly information about the object and its current settings. """
    return self.__repr__()
    
#Better to have a different class for each mode since they are not configured in the same way...

class Capability(object):
  """ A general class for camera capabilities.
  
  This is mostly a convenience class that allows to programmatically declare 
  the available capabilities.
  """
  def __init__(self, typ, name, code, caps):
    """
    :param typ: Capability type (eg ReadMode, AcqMode...)
    :param name: Capability name
    :param code: the Capability identifier (eg sdk.AC_READMODE_FVB)
    :param caps: the element of the Capability structure corresponding to typ (eg caps.ulReadModes)  
    """
    self._name = name # This will be the name as it appear to the user
    self._available = code & caps > 0
    self._code = code
    self._typ = typ

# ReadModes capabilities

class ReadModes(_AddCapabilities):
  """ This class is just container for the available ReadMode_XXX classes """
  # It's little more than an alias for _AddCapabilities
  def __init__(self, caps, ref = {}):
    super(ReadModes, self).__init__(caps, ref)
        
  def __repr__(self):
    return "Current Read mode : " + self.current._name

    
class ReadMode(Capability):
  """Base class for ReadMode_XXX classes.
  
  .. seealso::
     
    - :class:` ReadMode_Image`
    - :class:`ReadMode_SingleTrack`
    - :class:`ReadMode_FullVerticalBinning`
    - :class:` ReadMode_MultiTrack`
    - :class:`ReadMode_RandomTrack`
     
  """
  #Doesn't do anything but makes the class hierachy more sensible. 
  def __init__(self, typ, name, code, caps):
    super(ReadMode, self).__init__(typ, name, code, caps)  
    
class ReadMode_FullVerticalBinning(ReadMode):
  """Full Vertical Binning mode."""
  def __init__(self, typ, name, code, caps):
    super(ReadMode_FullVerticalBinning, self).__init__(typ, name, code, caps)
    
  def __call__(self):
    """Set the camera in FVB mode."""
    andorError(sdk.SetReadMode(0))
    self.ReadMode.current = self
    self.shape = [1]
    self.shape = self._cam.Detector.width
    self.pixels = self._cam.Detector.width
    
class ReadMode_SingleTrack(ReadMode):
  """Single Track mode."""
  def __init__(self, typ, name, code, caps):
    super(ReadMode_SingleTrack, self).__init__(typ, name, code, caps)
    
  def __call__(self, centre, height):
    """Set and configure the Readout Mode to Single Track.
    
    :param center: position of track center (in pixel)
    :param height: track height (in pixels)
    """
    andorError(sdk.SetReadMode(3))
    andorError(sdk.SetSingleTrack(centre, height))
    self._centre = centre
    self._height = height
    self._cam.ReadMode.current = self
    self.pixels = self._cam.Detector.width
    self.ndims = 1
    self.shape = [self._cam.Detector.width]
  
  @property
  def centre(self):
    """Set or query the track centre (can be called during acquisition)."""
    return self._centre
  @centre.setter
  @while_acquiring
  def centre(self, centre):
    andorError(sdk.SetSingleTrack(centre, self.height))
    self._centre = centre
  
  @property
  def height(self):
    """Set or query the track height (can be called during acquisition)."""
    return self._height
  @height.setter
  @while_acquiring
  def height(self, height):
    andorError(sdk.SetSingleTrack(self.centre, height))
    self._height = height
  
  @property
  def position(self):
    """Return a tuple (centre, height)."""
    return (self.centre, self.height)


class ReadMode_MultiTrack(ReadMode):
  """Multi-track mode."""
  def __init__(self, typ, name, code, caps):
    super(ReadMode_MultiTrack, self).__init__(typ, name, code, caps)
    
  def __call__(self, number, height, offset):
    """
    :param number: number of tracks
    :param height: height of tracks, in pixels
    :param offset: first track offset, in pixels
    """   
    andorError(sdk.SetReadMode(1))
    cdef int bottom, gap
    andorError(sdk.SetMultiTrack(number, height, offset, &bottom, &gap))
    self.number = number
    self.height = height
    self.offset = offset
    self.bottom = bottom
    self.gap = gap
    self._cam.ReadMode.current = self
    self.pixels = self._cam.Detector.width * self.number
    if self.number == 1:
      self.ndims = 1
      self.shape= [self._cam.Detector.width]
    else:
      self.ndims = 2
      self.shape= [self.number, self._cam.Detector.width]

class ReadMode_RandomTrack(ReadMode):
  """RandomTrack mode."""
  def __init__(self, typ, name, code, caps):
    super(ReadMode_RandomTrack, self).__init__(typ, name, code, caps)
    
  def __call__(self, numTracks, areas):
    """Set the camera in RandomTrack mode.
    
    :param int numTracks: number of tracks:
    :param areas: track parameters: tuple (start1, stop1, start2, stop2, ...)
    """
    #cdef np.ndarray[np.int_t, mode="c", ndim=1] areasnp = np.ascontiguousarray(np.empty(shape=6, dtype = np.int))
    cdef np.ndarray[np.int_t, mode="c", ndim=1] areasnp = np.ascontiguousarray(areas, dtype=np.int32)# np.int)
    andorError(sdk.SetReadMode(2))
    print(areasnp)
    andorError(sdk.SetRandomTracks(numTracks, &areasnp[0]))
    self.numTracks = numTracks
    self.areas = areas
    self._cam.ReadMode.current = self
    self.pixels = self._cam.Detector.width * self.numTracks
    if self.numTracks == 1:
      self.ndims = 1
      self.shape= [self._cam.Detector.width]
    else:
      self.ndims = 2
      self.shape= [self.numTracks, self._cam.Detector.width]
      
  def data_to_image(self, data):
    """Forms an image from Random Track data."""
    raise NotImplementedError
   
class ReadMode_Image(ReadMode):
  """Full image mode."""
  def __init__(self, typ, name, code, caps):
    super(ReadMode_Image, self).__init__(typ, name, code, caps)
    
  def __call__(self, binning=None, h=None, v=None, bint isolated_crop=False):
    """Set Readout mode to Image, with optional binning and sub-area coordinates.
    
    NOTE: binning and subarea not implemented yet. 
    
    :param binning: (hbin, vbin)
    :param h: (left, right) horizontal coordinates (in binned pixels)
    :param v: (top, bottom) vertical coordinates
    :param isolated_crop: ?
    :type isolated_crop: bool
    
    .. Warning:: this nay be buggy/not working
    
    """
    #NOTE: this is probably buggy
    andorError(sdk.SetReadMode(4))
    # process **kwargs and set Image parameters if they are defined:  
    (hbin, vbin) = (1, 1) if binning is None else binning
    h = (1, self._cam.Detector.width) if h is None else h
    v = (1, self._cam.Detector.height) if v is None else v
    #(hsize, vsize) = self._cam.Detector.size if size is None else size
    #(h0, v0) = (1, 1) if lower_left is None else lower_left
    #if not None in (binning, size, lower_left):
    andorError(sdk.SetImage(hbin, vbin, h[0], h[1], v[0], v[1]))
    #if isolated_crop:
    #  andorError(SetIsolatedCropMode(isolated_crop, hsize * hbin, vbin, hbin))
    
    self._cam.ReadMode.current = self
    self.shape = [h[1] - h[0] + 1, v[1] - v[0] + 1]
    self.pixels = self.shape[0] * self.shape[1]
    self.ndims = 2
    
    
# AcqModes capabilities
# The AcqMode class provide functions that are common to all modes (status, start, stop),
# while the AcqMode_XXX classes provide mode-specific functions (initialisation and doc)
# NOTE : the "typ" parameters could be removed here...
# To change the mode or change the parameters, just call the object:
# >>> main.AcqMode.Kinetic(params)
# The first call to an SDK function will raise an error if it can't be change, so we don't need to worry about that.
# Then to start the acquisition:
# >>> main.Acquire.start()
# >>> main.Acquire.status
# >>> main.Acquire.stop()
# main.Acquire is just a reference to the current AcqMode object.

class AcqModes(_AddCapabilities):
  """Container for the available AcqMode_XXX classes. """
  # It's little more than an alias for _AddCapabilities
  def __init__(self, caps, ref = {}):
    super(AcqModes, self).__init__(caps, ref)
    self.current = None
    
  def __repr__(self):
    return "Current Acquisition mode : " + self.current._name

class AcqMode(Capability):
  """Base class for acquisition modes AcqMode_XXX.
  
  .. seealso:
     
     - :class:`AcqMode_Video`
     - :class:`AcqMode_Single`
     - :class:`AcqMode_Accumulate`
     - :class:`AcqMode_Kinetic`

  """
  # The parent class for all acquisition modes. 
  # Includes methods to start/stop the acquisition and collect the acquired data
  def __init__(self, typ, name, code, caps):
    super(AcqMode, self).__init__(typ, name, code, caps)
    self.current = None
    self.rollover = False
    self.snapshot_count = 0
    self.last_snap_read = 0
    #self.Trigger = _AddCapabilities(self._cam.Info.capabilities.TriggerModes, {})

  # Acquisition control
  
  @property
  def status(self):
    """Return the camera status code and corresponding message."""
    cdef int status
    andorError(sdk.GetStatus(&status))
    return (status, ERROR_CODE[status])
  
  @property
  def running(self):
    """Query whether the camera is busy (ongoing acquisition or video).""" 
    if self.status[1] is "DRV_ACQUIRING":
      return True
    else:
      return False
  
  def start(self):
    """Start the acquisition."""
    andorError(sdk.StartAcquisition())
    self.start_time = time.time()
    self.snapshot_count += 1
    
  def stop(self):
    """Stop an ongoing acquisition."""
    andorError(sdk.AbortAcquisition(), ignore=('DRV_IDLE'))
    
  def wait(self, new_data=False):
    """Wait either for new data to be available or for the whole acquisition sequence (default) to terminate.
    
    :param bool new_data: if True, pause until a new image is available in the buffer.
                     if False, pause until the whole acquisition terminates.
    
    Press :kbd:`Ctrl+C` to stop waiting.
    
    .. Warning:: This is not thread-safe!    
    """
    try:
      andorError(sdk.WaitForAcquisition())
      if not new_data:
        while self.status[1] is 'DRV_ACQUIRING':
          andorError(sdk.WaitForAcquisition())
    except KeyboardInterrupt:
      pass
    
  def __call__(self):
    """Set the camera acquisition mode. 
    
    Called by sub-classes.
    """
    # Stuff to do for all modes when calling the method, namely set 'main.AcqMode.current' and 'main.Acquire' to the current mode
    self._cam._AcqMode.current = self
    self._cam.Acquire = self
    self.snapshot_count = 0
    
  @property
  def max_exposure(self):
    """Return the maximum settable exposure time, in seconds."""
    cdef float MaxExp
    andorError(sdk.GetMaximumExposure(&MaxExp))
    return MaxExp
  
  # Data collection
  
  @property
  def size_of_circular_buffer(self):
    """Return the maximum number of images the circular buffer can store based on the current acquisition settings."""
    cdef sdk.at_32 index
    andorError(sdk.GetSizeOfCircularBuffer(&index))
    return index
    
  @property
  def images_in_buffer(self):
    """Return information on the number of available images in the circular buffer.
    
   This information can be used with GetImages to retrieve a series of images. If any
   images are overwritten in the circular buffer they no longer can be retrieved and the
   information returned will treat overwritten images as not available.
   """
    cdef sdk.at_32 first, last
    andorError(sdk.GetNumberAvailableImages(&first, &last))
    return {"first": first, "last": last}

  @property
  def new_images(self):
    """Return information on the number of new images (i.e. images which have not yet been retrieved) in the circular buffer.
    
    This information can be used with GetImages to retrieve a series of the latest images. 
    If any images are overwritten in the circular buffer they can no longer be retrieved
    and the information returned will treat overwritten images as having been retrieved.
    """
    cdef sdk.at_32 first, last
    andorError(sdk.GetNumberNewImages(&first, &last))
    return {"first": first, "last": last}
      
  #@rollover
  def Newest(self, n=1, type=16):
    """Returns a data array with the most recently acquired image(s) in any acquisition mode.
    
    :param number: number of images to retrieve
    :param type: whether to return the data as 16 or 32-bits integers (16 [default] or 32)
    """
    cdef np.ndarray[np.uint16_t, mode="c", ndim=1] data16
    cdef np.ndarray[np.int32_t, mode="c", ndim=1] data32
    if n == 1:
      npixels = self._cam.ReadMode.current.pixels
      if type == 16:
        data16 = np.ascontiguousarray(np.empty(shape=npixels, dtype=np.uint16))
        andorError(sdk.GetMostRecentImage16(&data16[0], npixels))
        data = data16
      else:
        data32 = np.ascontiguousarray(np.empty(shape=npixels, dtype=np.int32))
        andorError(sdk.GetMostRecentImage(&data32[0], npixels))
        data = data32
      return data.reshape(self._cam.ReadMode.current.shape)
    elif n > 1:
      most_recent = self.images_in_buffer['last']
      return self.Images(most_recent - n + 1, most_recent, type=type)
    else:
      raise ValueError('Invalid number of images: ' + str(n))
      
  
  @rollover
  def Oldest(self, type=16):
    """Retrieve the oldest available image from the circular buffer.
    
    Once the oldest image has been retrieved it is no longer available,
    and calling GetOldestImage again will retrieve the next image.
    This is a useful function for retrieving a number of images.
    For example if there are 5 new images available, calling it 5 times will retrieve them all.
    
    :param type: whether to return the data as 16 or 32-bits integers (16 [default] or 32)
    """
    npixels = self._cam.ReadMode.current.pixels
    cdef np.ndarray[np.uint16_t, mode="c", ndim=1] data16
    cdef np.ndarray[np.int32_t, mode="c", ndim=1] data32
    if type == 16:
      data16 = np.ascontiguousarray(np.empty(shape=npixels, dtype=np.uint16))
      andorError(sdk.GetOldestImage16(&data16[0], npixels))
      return data16
    else:
      data32 = np.ascontiguousarray(np.empty(shape=npixels, dtype=np.int32))
      andorError(sdk.GetOldestImage(&data32[0], npixels))
      return data32  
  
  @rollover
  def Images(self, first, last, type=16):
    """Return the specified series of images from the circular buffer.
    
    If the specified series is out of range (i.e. the images have been
    overwritten or have not yet been acquired) then an error will be returned.
    
    :param first: index of first image in buffer to retrieve.
    :param last: index of last image in buffer to retrieve.
    :param type: whether to return the data as 16 or 32-bits integers (default: 16)
    """
    nimages = last - first + 1
    pixels_per_image = self._cam.ReadMode.current.pixels
    total_pixels = nimages * pixels_per_image
    final_shape = [nimages] + self._cam.ReadMode.current.shape
    cdef np.ndarray[np.uint16_t, mode="c", ndim=1] data16
    cdef np.ndarray[np.int32_t, mode="c", ndim=1] data32
    cdef np.int32_t validfirst, validlast
    if type == 16:
      data16 = np.ascontiguousarray(np.empty(shape=total_pixels, dtype=np.uint16))
      andorError(sdk.GetImages16(first, last, &data16[0], total_pixels, &validfirst, &validlast))
      data = data16
    else:
      data32 = np.ascontiguousarray(np.empty(shape=total_pixels, dtype=np.int32))
      andorError(sdk.GetImages(first, last, &data32[0], total_pixels, &validfirst, &validlast))
      data = data32
    self.valid = {'first': validfirst, 'last': validlast}
    return data.reshape(final_shape)

  @rollover
  def GetAcquiredData(self, type=16):
    """Return the whole data set from the last acquisition.
    
    GetAcquiredData should be used once the acquisition is complete to retrieve all the data from the series.
    This could be a single scan or an entire kinetic series.
    
    :param type: (16 or 32) whether to return the data as 16 or 32-bits integers (default: 16)
    """   
    pixels_per_image = self._cam.ReadMode.current.pixels
    nimages = self.nimages
    total_pixels = nimages * pixels_per_image
    final_shape = [nimages] + self._cam.ReadMode.current.shape
    cdef np.ndarray[np.uint16_t, mode="c", ndim=1] data16
    cdef np.ndarray[np.int32_t, mode="c", ndim=1] data32
    if type == 16:
      data16 = np.ascontiguousarray(np.empty(shape=total_pixels, dtype = np.uint16))
      andorError(sdk.GetAcquiredData16(&data16[0], total_pixels))
      data = data16
    else:
      data32 = np.ascontiguousarray(np.empty(shape=total_pixels, dtype = np.int32))
      andorError(sdk.GetAcquiredData(&data32[0], total_pixels))
      data = data32
    self.last_acquired_data = data.reshape(final_shape) 
    return self.last_acquired_data

  def Video(self):
    """Switch to Video mode and start acquiring."""
    self = self._cam._AcqMode.Video
    self.__call__(start=True)
    
  def Kinetic(self, numberKinetics, kineticCycleTime, numberAccumulation = 1, accumulationCycleTime = 0, safe=True):
    """Switch to and configure Kinetic acquisition."""
    self = self._cam._AcqMode.Kinetic
    self.__call__(numberKinetics, kineticCycleTime, numberAccumulation, accumulationCycleTime,safe=safe)
  
  def Single(self):
    """Switch to Single mode."""
    #self.stop()
    self = self._cam._AcqMode.Single
    self.__call__()

  def Accumulate(self, numberAccumulation, accumulationCycleTime, safe=True):
    """Switch to and configure Accumulate acquisition."""
    self = self._cam._AcqMode.Accumulate
    self.__call__(numberAccumulation, accumulationCycleTime, safe=safe)
    
  def save(self, filename, dataset, data, metadata_func=None):
    """Save data and associated metadata to an HDF5 file.
    
    :param string filename: name of the H5 file (must already exist).
    :param string dataset_name: name of the dataset (must not already exist).
    :param data: any HDF5 compatible data (eg cam.Acquire.Newest())
    
    The following metadata are also recorded: 
      - acquisition mode
      - exposure time
      - EM gain
      - time (string).
    """
    with h5py.File(filename, 'r+') as f:
      f.create_dataset(dataset, data=data)
      f[dataset].attrs['mode'] = self._name
      f[dataset].attrs['exposure'] = self._cam.exposure
      f[dataset].attrs['em_gain'] = self._cam.EM._read_gain_from_camera()
      f[dataset].attrs['created'] = time.strftime("%d/%m/%Y %H:%M:%S")
      if metadata_func is not None:
        metadata_func(f[dataset])
    
  def take_multiple_exposures(self, exposures):
    """Take a series of single images with varying exposure time.
    
    :param exposures: a tuple of exposure times.
    
    :returns: a numpy array of length len(exposures).
    """
    if self._name is "Video":
      video = True
      self.stop()
      self.Single()
    data = []
    for e in exposures:
      self._cam.exposure = e
      self.start()
      self.wait()
      data.append(self.Newest())
    if video:
      self.Video()
      self.start()
    return np.array(data)
        
    
class AcqMode_Single(AcqMode):
  """ Set the camera in Single Acquisition mode.
  
  The snapshot_count counter is reset when Single() is called, 
  and incremented every time snap() (or equivalently start()) is called.
  
  Arguments: None
  """
  def __init__(self, typ, name, code, caps):
    super(AcqMode_Single, self).__init__(typ, name, code, caps)
    self.shape = []
    self.ndims = 0
    self.nimages = 1
    
  def __call__(self, safe=True):
    """Set the camera in Single Acquisition mode.
    
    :param bool safe: if False, any ongoing acquisition will be stopped;
                 if True (default) an error will be raised.
    """
    if not safe:
      self.stop()
    andorError(sdk.SetAcquisitionMode(1))
    super(AcqMode_Single, self).__call__()
    
  def __repr__(self):
    return "Snapshot acquisition mode."
    
    
  def snap(self, wait=True, type=16):
    """Take a single image. 
    
    :param wait: if True, wait for the acquisition to complete and return the data.
    :param type: (16 or 32) whether to return the data as 16 or 32-bits integers (default: 16)
    """
    self.start()
    if wait:
      self.wait()
      return self.Newest(type)
    
class AcqMode_Accumulate(AcqMode):
  """Set the camera in Accumulate mode.
  
  It's a good idea to retrieve the data as 32bits integers."""
  def __init__(self, typ, name, code, caps):
    #
    super(AcqMode_Accumulate, self).__init__(typ, name, code, caps)
    self.shape = []
    self.ndims = 0
    self.nimages = 1
    self._kinetic = False # whether the accumulation cycle is part of a kinetic sequence.
    
  def __call__(self, numberAccumulation, accumulationCycleTime, safe=True):
    """ Set the camera in Accumulate mode.
    
    :param int numberAccumulation: Number of accumulations
    :param int accumulationCycleTime: cycle time
    :param bool safe: if True, raises an error if an acquisition is ongoing.
    """
    if not safe:
      self.stop()
    if not self._kinetic:
      andorError(sdk.SetAcquisitionMode(2))
    andorError(sdk.SetNumberAccumulations(numberAccumulation))
    andorError(sdk.SetAccumulationCycleTime(accumulationCycleTime))
    self.numberAccumulation = numberAccumulation
    self.accumulationCycleTime = accumulationCycleTime
    super(AcqMode_Accumulate, self).__call__()
    
  def __repr__(self):
    return "Accumulate acquisition with settings: \n" + \
           "  Number of Accumulations: "+ str(self.numberAccumulation) +"\n" \
           "  Cycle time: "+ str(self._cam.acquisitionTimings['accumulate']) +"."
  
  def save(self, filename, dataset_name, metadata_func=None):
    """Save data and associated metadata from the last completed acquisition to an HDF5 file.
    
    :param string filename: name of the H5 file (must already exist).
    :param string dataset_name: name of the dataset (must not already exist).
    :param metadata_func: optional function to save more metadata. Takes a :class:`h5py.Group` as unique argument.
    
    The following metadata are also recorded: 
      - acquisition mode
      - exposure time
      - EM gain
      - time (string)
      - accumulation number and cycle time
    """
    def save_metadata(h5group, metadata_func=None):
      h5group.attrs['accumulate_cycle_time'] = self._cam.acquisitionTimings['accumulate']
      h5group.attrs['accumulate_number'] = self.numberAccumulation
      if metadata_func is not None:
        metadata_func(h5group)
    data = self.GetAcquiredData()
    super(AcqMode_Accumulate, self).save(filename, dataset_name, data, save_metadata)
    

class AcqMode_Video(AcqMode):
  """ Set the camera in Video (Run Till Abort) mode.
  
  Arguments: None
  """
  def __init__(self, typ, name, code, caps):
    super(AcqMode_Video, self).__init__(typ, name, code, caps)
    self.shape = []
    self.ndims = 0
    self.nimages = 1
    
  def __call__(self, start=True, live=False):
    andorError(sdk.SetAcquisitionMode(5))
    super(AcqMode_Video, self).__call__()
    if start:
      super(AcqMode_Video, self).start()
    if live:
      self._cam.Display.start()
      
  def __repr__(self):
    return "<Video acquisition mode>"

class AcqMode_Kinetic(AcqMode_Accumulate):
  """Kinetic mode. 

  Callable.
  """
  def __init__(self, typ, name, code, caps):
    super(AcqMode_Kinetic, self).__init__(typ, name, code, caps)
    self._kinetic = True
    
  def __call__(self, numberKinetics, kineticCycleTime, numberAccumulation = 1, accumulationCycleTime = 0, safe=True):
    """Set the camera in Kinetic mode.
    
    :param numberKinetics: number of images in kinetic sequence
    :param kineticCycleTime: : interval between images in kinetic sequence, in seconds
    :param numberAccumulation: number of images to accumulate for each imahe in kinetic sequence
    :param accumulationCycleTime: interval between accumulated images, in seconds
    :param safe: set to False to cancel any ongoing acquisition.
    """
    if not safe:
      self.stop()
    andorError(sdk.SetAcquisitionMode(3))
    andorError(sdk.SetNumberKinetics(numberKinetics))
    andorError(sdk.SetKineticCycleTime(kineticCycleTime))
    self.numberKinetics = numberKinetics
    self.kineticCycleTime = kineticCycleTime
    self.ndims = 1
    self.shape = [numberKinetics,]
    self.nimages = numberKinetics
    # Now call Accumulate()
    super(AcqMode_Kinetic, self).__call__(numberAccumulation, accumulationCycleTime, safe)
    
    # NOTE : Should check the value of GetAcquisitionTimings 
  
  def save(self, filename, dataset_name):
    """Save data and associated metadata from the last completed acquisition to an HDF5 file.
    
    :param string filename: name of the H5 file (must already exist).
    :param string dataset_name: name of the dataset (must not already exist).
    :param metadata_func: optional function to save more metadata. Takes a :class:`Group` as unique argument.
    
    The following metadata are also recorded: 
      - acquisition mode
      - exposure time
      - EM gain
      - time (string)
      - accumulation number and cycle time
      - Kineatic number and cycle time
    """
    def metadata_func(h5group):
      h5group.attrs['kinetic_cycle_time'] = self._cam.acquisitionTimings['kinetic']
      h5group.attrs['kinetic_number'] = self.numberKinetics
    # data will be collected by Accumulate.save()
    super(AcqMode_Kinetic, self).save(filename, dataset_name, metadata_func)
    
  
  def __repr__(self):
    if self.numberAccumulation > 1:
      acc_str = "  Number of Accumulation: " + str(self.numberAccumulation) + "\n" \
            + "  Accumulation cycle time: " + str(self.accumulationCycleTime)
    else:
      acc_str = "  No Accumulation"
    return("Kinetic acquisition with settings : \n" \
            + "  Number in Kinetic series: " + str(self.numberKinetics) + "\n" \
            + "  Kinetic cycle time: " + str(self.kineticCycleTime) + "\n" \
            + acc_str)       
            
class TriggerMode(Capability):
  
  def __init__(self, typ, name, code, caps, trigger_code):
    super(TriggerMode, self).__init__(typ, name, code, caps)
    self._inverted = False
    self._trigger_code = trigger_code
    
  def __call__(self):
    """Call with no argument to set the trigger mode."""
    andorError(sdk.SetTriggerMode(self._trigger_code))
    
  @property
  def inverted(self):
    """This property will set whether an acquisition will be triggered on a rising (False, default) or falling (True) edge external trigger."""
    return self._inverted
  @inverted.setter
  def inverted(self, bint value):
    andorError(sdk.SetTriggerInvert(value))
    self._inverted = value
    
  def __repr__(self):
    return "<Trigger mode>"

            
class Capabilities:
  """Container for camera capabilities.
  
  Retrieves and parses the SDK's AndorCapabilities struct, returning
  dictionaries indicating which capabilities are available.
  
  The following sets of capabilities are completely parsed:
    - ``AcqModes``
    - ``ReadModes``
    - ``ReadModesWithFrameTransfer``
    - ``TriggerModes``
    - ``CameraType``
    - ``PixelMode``
    - ``PCICard``
    - ``EMGain``
  
  The following are only partially parsed:
    - ``SetFunctions`` (see also ``Fan`` and ``Temperature``)
    - ``GetFunctions`` (see also ``Fan`` and ``Temperature``)
    - ``Features``
  
  and some of the relevant capabilities are present in the ``Fan`` 
  and ``Temperature`` dictionaries.

  Finally, when available, :class:`AcqMode`, :class:`ReadMode` and 
  :class:`TriggerMode` objects are created as the properties ``_AcqModes``,
  ``_ReadModes`` and ``_TriggerModes``.
  
  """
  # Should we initialise caps here?
  def __init__(self):
    cdef sdk.AndorCapabilities caps
    caps.ulSize = cython.sizeof(caps)
    andorError(sdk.GetCapabilities(&caps))
    self.AcqModes = {
         "Single": sdk.AC_ACQMODE_SINGLE & caps.ulAcqModes > 0, 
         "Video": sdk.AC_ACQMODE_VIDEO & caps.ulAcqModes > 0,
         "Accumulate": sdk.AC_ACQMODE_ACCUMULATE & caps.ulAcqModes > 0,
         "Kinetic": sdk.AC_ACQMODE_KINETIC & caps.ulAcqModes > 0,
         "Frame transfer": sdk.AC_ACQMODE_FRAMETRANSFER & caps.ulAcqModes > 0,
         "Fast kinetics": sdk.AC_ACQMODE_FASTKINETICS & caps.ulAcqModes > 0,
         "Overlap": sdk.AC_ACQMODE_OVERLAP & caps.ulAcqModes > 0}
    self.ReadModes = {
          "Full image": sdk.AC_READMODE_FULLIMAGE & caps.ulReadModes > 0,
          "Subimage": sdk.AC_READMODE_SUBIMAGE & caps.ulReadModes > 0,
          "Single track": sdk.AC_READMODE_SINGLETRACK & caps.ulReadModes > 0,
          "Full vertical binning": sdk.AC_READMODE_FVB & caps.ulReadModes > 0,
          "Multi-track": sdk.AC_READMODE_MULTITRACK & caps.ulReadModes > 0,
          "Random track": sdk.AC_READMODE_RANDOMTRACK & caps.ulReadModes > 0,
          "Multi track scan": sdk.AC_READMODE_MULTITRACKSCAN & caps.ulReadModes > 0}
    self.ReadModesWithFrameTransfer = {
          "Full image": sdk.AC_READMODE_FULLIMAGE & caps.ulFTReadModes > 0,
          "Subimage": sdk.AC_READMODE_SUBIMAGE & caps.ulFTReadModes > 0,
          "Single track": sdk.AC_READMODE_SINGLETRACK & caps.ulFTReadModes > 0,
          "Full vertical binning": sdk.AC_READMODE_FVB & caps.ulFTReadModes > 0,
          "Multi-track": sdk.AC_READMODE_MULTITRACK & caps.ulFTReadModes > 0,
          "Random track": sdk.AC_READMODE_RANDOMTRACK & caps.ulFTReadModes > 0,
          "Multi track scan": sdk.AC_READMODE_MULTITRACKSCAN & caps.ulFTReadModes > 0}
    self.TriggerModes = {
          "Internal": sdk.AC_TRIGGERMODE_INTERNAL & caps.ulTriggerModes > 0,
          "External": sdk.AC_TRIGGERMODE_EXTERNAL & caps.ulTriggerModes > 0,
          "External with FVB + EM": sdk.AC_TRIGGERMODE_EXTERNAL_FVB_EM & caps.ulTriggerModes > 0,
          "Continuous": sdk.AC_TRIGGERMODE_CONTINUOUS & caps.ulTriggerModes > 0,
          "External start": sdk.AC_TRIGGERMODE_EXTERNALSTART & caps.ulTriggerModes > 0,
          "External exposure": sdk.AC_TRIGGERMODE_EXTERNALEXPOSURE & caps.ulTriggerModes > 0,
          "Inverted": sdk.AC_TRIGGERMODE_INVERTED & caps.ulTriggerModes > 0,
          "Charge shifting": sdk.AC_TRIGGERMODE_EXTERNAL_CHARGESHIFTING & caps.ulTriggerModes > 0}
    self._TriggerModes = (
          TriggerMode("", "Internal", 1, 1, 0),
          TriggerMode("", "External", sdk.AC_TRIGGERMODE_EXTERNAL, caps.ulTriggerModes, 1),
          TriggerMode("", "External_FVB", sdk.AC_TRIGGERMODE_EXTERNAL_FVB_EM, caps.ulTriggerModes, 9),
          TriggerMode("", "Continuous", sdk.AC_TRIGGERMODE_CONTINUOUS, caps.ulTriggerModes, 10),
          TriggerMode("", "External start", sdk.AC_TRIGGERMODE_EXTERNALSTART, caps.ulTriggerModes, 6),
          TriggerMode("", "External_Exposure", sdk.AC_TRIGGERMODE_EXTERNALEXPOSURE, caps.ulTriggerModes, 7),
          TriggerMode("", "External_Charge_Shifting", sdk.AC_TRIGGERMODE_EXTERNAL_CHARGESHIFTING, caps.ulTriggerModes, 12)
          )
    self._AcqModes = (AcqMode_Single("AcqMode", "Single", sdk.AC_ACQMODE_SINGLE, caps.ulAcqModes),
          AcqMode_Video("AcqMode", "Video", sdk.AC_ACQMODE_VIDEO, caps.ulAcqModes),
          AcqMode_Accumulate("AcqMode", "Accumulate", sdk.AC_ACQMODE_ACCUMULATE, caps.ulAcqModes),
          AcqMode_Kinetic("AcqMode", "Kinetic", sdk.AC_ACQMODE_KINETIC, caps.ulAcqModes),
          )
    self._ReadModes = (
      ReadMode_Image("ReadMode", "Image", sdk.AC_READMODE_FULLIMAGE, caps.ulReadModes),
      #ReadMode_SubImage("ReadMode", "Subimage", sdk.AC_READMODE_SUBIMAGE, caps.ulReadModes),
      ReadMode_SingleTrack("ReadMode", "SingleTrack", sdk.AC_READMODE_SINGLETRACK, caps.ulReadModes),
      ReadMode_FullVerticalBinning("ReadMode", "FullVerticalBinning", sdk.AC_READMODE_FVB, caps.ulReadModes),
      ReadMode_MultiTrack("ReadMode", "MultiTrack", sdk.AC_READMODE_MULTITRACK, caps.ulReadModes),
      ReadMode_RandomTrack("ReadMode", "RandomTrack", sdk.AC_READMODE_RANDOMTRACK, caps.ulReadModes),
      #ReadMode_MultiTrackScan("ReadMode", "MultiTrackScan", sdk.AC_READMODE_MULTITRACKSCAN, caps.ulReadModes)
       )
    self.CameraType = CameraTypes[caps.ulCameraType]
    self.PixelModes = {
      "8 bits": sdk.AC_PIXELMODE_8BIT & caps.ulPixelMode > 0, 
      "14 bits": sdk.AC_PIXELMODE_14BIT & caps.ulPixelMode > 0,
      "16 bits": sdk.AC_PIXELMODE_16BIT & caps.ulPixelMode > 0,
      "32 bits": sdk.AC_PIXELMODE_32BIT & caps.ulPixelMode > 0,
      "Greyscale": sdk.AC_PIXELMODE_MONO & caps.ulPixelMode > 0,
      "RGB": sdk.AC_PIXELMODE_RGB & caps.ulPixelMode > 0,
      "CMY": sdk.AC_PIXELMODE_CMY & caps.ulPixelMode > 0}
    self.SetFunctions = {
      "Extended EM gain range": sdk.AC_SETFUNCTION_EMADVANCED & caps.ulSetFunctions > 0,
      "Extended NIR mode": sdk.AC_SETFUNCTION_EXTENDEDNIR & caps.ulSetFunctions > 0,
      "High capacity mode": sdk.AC_SETFUNCTION_HIGHCAPACITY & caps.ulSetFunctions > 0}
    self.Fan = {
      "Fan can be controlled": sdk.AC_FEATURES_FANCONTROL & caps.ulFeatures >0,
      "Low fan setting": sdk.AC_FEATURES_MIDFANCONTROL & caps.ulFeatures >0}
    self.Temperature = {
      "Temperature can be read during acquisition": sdk.AC_FEATURES_TEMPERATUREDURINGACQUISITION & caps.ulFeatures >0,
      "Temperature can be read": sdk.AC_GETFUNCTION_TEMPERATURE & caps.ulGetFunctions >0,
      "Valid temperature range can be read": sdk.AC_GETFUNCTION_TEMPERATURERANGE & caps.ulGetFunctions >0}
    self.PCICard = {"Maximum speed (Hz)": caps.ulPCICard}
    self.EMGain = {
      "8-bit DAC settable": sdk.AC_EMGAIN_8BIT & caps.ulEMGainCapability > 0,
      "12-bit DAC settable": sdk.AC_EMGAIN_12BIT & caps.ulEMGainCapability > 0,
      "Gain setting represent a linear gain scale. 12-bit DAC used internally": sdk.AC_EMGAIN_LINEAR12
 & caps.ulEMGainCapability > 0,
      "Gain setting represents the real EM Gain value. 12-bit DAC used internally": sdk.AC_EMGAIN_REAL12
 & caps.ulEMGainCapability > 0,

      }

CameraTypes = {0: "PDA", 1: "iXon", 2: "ICCD", 3: "EMCCD", 4: "CCD", 5: "iStar", 6: "Not Andor Camera", 
7: "IDus", 8: "Newton", 9: "Surcam", 10: "USBiStar", 11: "Luca", 13: "iKon", 14: "InGaAs",
15: "iVac", 17: "Clara"}

PixelModes = {0: "8 bits", 1: "14 bits", 2: "16 bits", 3: "32 bits"}   
  
TEMPERATURE_MESSAGES = (20034, 20035, 20036, 20037, 20040)
  
ERROR_CODE = {
    20001: "DRV_ERROR_CODES",
    20002: "DRV_SUCCESS",
    20003: "DRV_VXNOTINSTALLED",
    20006: "DRV_ERROR_FILELOAD",
    20007: "DRV_ERROR_VXD_INIT",
    20010: "DRV_ERROR_PAGELOCK",
    20011: "DRV_ERROR_PAGE_UNLOCK",
    20013: "DRV_ERROR_ACK",
    20024: "DRV_NO_NEW_DATA",
    20026: "DRV_SPOOLERROR",
    20034: "DRV_TEMP_OFF",
    20035: "DRV_TEMP_NOT_STABILIZED",
    20036: "DRV_TEMP_STABILIZED",
    20037: "DRV_TEMP_NOT_REACHED",
    20038: "DRV_TEMP_OUT_RANGE",
    20039: "DRV_TEMP_NOT_SUPPORTED",
    20040: "DRV_TEMP_DRIFT",
    20050: "DRV_COF_NOTLOADED",
    20053: "DRV_FLEXERROR",
    20066: "DRV_P1INVALID",
    20067: "DRV_P2INVALID",
    20068: "DRV_P3INVALID",
    20069: "DRV_P4INVALID",
    20070: "DRV_INIERROR",
    20071: "DRV_COERROR",
    20072: "DRV_ACQUIRING",
    20073: "DRV_IDLE",
    20074: "DRV_TEMPCYCLE",
    20075: "DRV_NOT_INITIALIZED",
    20076: "DRV_P5INVALID",
    20077: "DRV_P6INVALID",
    20083: "P7_INVALID",
    20089: "DRV_USBERROR",
    20099: "DRV_BINNING_ERROR",
    20990: "DRV_NOCAMERA",
    20991: "DRV_NOT_SUPPORTED",
    20992: "DRV_NOT_AVAILABLE"
}
