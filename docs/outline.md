#

## Intro -- what and why
- Integration and the need for content
  - Challenge 1
    - Systems are composed of many design blocks (processor core, interconnect, comm controller)
    - Require complex (individually and/or in aggregate) programming to configure and operate
    - Becomes most apparent with integration teams -- SoC, Emulation, Firmware, Post-Si
  - Challenge 2
    - Drift -- one team tests one way, another differently. One small config/programming difference cause device to behave very differently
    - Major cause of integration headaches
  - Bottom line: need consistent content across several languages and methodologies
  - Challenges -- many languages, different requirements
- PSS is visible solution for making *tests* portable
  - PSS test description -> generator -> test implemented in one of many languages
    - Need to show 'randomization', 'register programming' in each Action bubble
    - Two key pieces: scenario/decision ; realization / device-driver / device-utility
  - Brief 'PSS elements'
    - Component tree provides structure
    - Actions define resource and data-flow relationships and make random choices
    - Procedural code calling external functions and interacting with registers/memory carry out decisions
  - What is a test?
    - limited parameterization
    - autonomous - exercises the design within the given parameters, checking as it goes
    - clear pass/fail
- PSS adoption requirements and challenges
  - Requirements
    - Adopt PSS language for test descriptions
    - Have (or create) PSS content for all devices that the test touches
    - *Be creating tests*
  - Challenges
    - Don't always need "tests"
      - Misson-mode firmware exercises the design, but isn't a *test*
    - Might not be able/willing to create full tests in PSS
    - Might not have PSS for all devices
- Taking PSS beyond *test* reuse (how does it work)
  - Separate 'realization' from 'scenario' in PSS (at this point, it's a simple separation)
    - Scenario stays in actions
    - Realization moves to functions in components, called by actions
    -> Need to get 'operation model' in somewhere here
  - Generate reusable utility functions
    - SV class with tasks
    - C functions
    - Python
    - ...
  - Can still directly use in PSS scenarios
- Bottom line: 
  - PSS gives us a single source of truth for content that can target any language
  - More available PSS content enables PSS adoption for test scenarios

## Getting Technical: Operation Model Anatomy
- Key requirements
  - API(s) for environment to call the operation model
    - Perform a device operation
    - Notify operation model of an event
  - API(s) for calling out to the environment
  - Mechanism to initialize operation model state
  - Place to hold state (eg register aperture addresses)
- Language-specific mappings
  - SystemVerilog
    - Interface class with methods for export API
    - Interface class with methods for import API
    - Factory class for initialization -> returns export API instance
      - Returned handle holds the state
  - C
    - global functions (<comp_t>_<func>) for export
    - global functions (<func>) for import
    - '_ctor' function for initialization
      - opaque struct holds the state


## Lab 1 - Core Structure
- PSS Description
  - Component tree
  - initialization function 
  - Public functions, import functions
- Generating output
  - pssc command
  - available output flavors
  - 
- Environment integration
  - SystemVerilog
  - C
  - ...
- Lab
  - Define model
  - Generate code
  - Observe

## Lab 2 - Registers and Memory
- PSS register model and memory-access function overview
  - 
- Creating register models
- Register-operation details
  - 
- Lab
  - Create PSS register model from SystemRDL (or Rubix)
  - Implement programming sequence
  - Generate output and observe 
