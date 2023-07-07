## 6.1.2 (2023-07-07)

### Fix

- check the type of bus stop before returning it from registries
- **BusStopRegistry**: prevent bus stop registry to unregister None bus stops
- **BusStopRegistry**: raise exception is the bus resolved is none before trying to register it
- fix bus resolvers typing

## 6.1.1 (2023-07-04)

### Fix

- fix some dependencies versions

## 6.1.0 (2023-07-03)

### Feat

- add yandil bus stop resolver

## 6.0.1 (2023-05-20)

### Fix

- add root passenger id to passenger tracking

## 6.0.0 (2023-05-17)

### BREAKING CHANGE

- changed query bus and query bus engines initialization
- changed bus and bus engines initialization
- command buses and engines initialization changed

### Feat

- allow different bus stops to handle plain dataclasses in order to allow working with mapped passengers
- **Bus**: allow transport for plain dataclasses also in order to allow working with mapped passengers
- add declarative passenger mapper

### Fix

- **Passenger**: fix from_data_dict to work with an input data copy in order to avoid modifying the original data
- **BusStopAddressRegistrationSupervisor**: get address to register from env
- **BusStopAddressRegistry**: fix abstract bus stop address registry abstract class declaration
- **passenger-resolver**: fix passenger resolver typing

### Refactor

- **passenger_resolvers**: remove type checking on passenger resolving to allow working with mapped passengers
- add memory queue factory to simplify memory queue buses and engines
- Add internal passenger registry to simplify dependencies
- refactors to adapt code to new  bus stop module
- simplify query bus and bus engines
- simplify event terminal buses and engines
- simplify command terminal buses and engines
- move bus stop components to its own module
- adapt source code to change from class utils components to functions
- change passenger class utilities to functions instead of classes
- **Bus**: change bus to set the root passenger id to the passenger not the distributed id
- **PassengerReceiver**: change passenger receiver to set the root passenger id instead of the distributed id
- **Passenger**: change distributed id by root passenger id
- **distributed.py**: change distributed functions by context ones

## 5.1.0 (2023-03-17)

### Feat

- make distributed id work with serialization/deserialization
- add distributed id on bus transport
- add distributed id on passenger receivers
- add distributed id functions
- **Passenger**: add distributed id

## 5.0.0 (2023-03-10)

## 4.0.0 (2023-01-13)

## 3.0.2 (2023-01-03)

## 3.0.1 (2023-01-03)

## 3.0.0 (2022-12-25)

## 2.1.1 (2022-12-19)

## 2.1.0 (2022-12-18)

## 2.0.1 (2022-12-17)

## 2.0.0 (2022-10-31)

## 1.0.0 (2022-08-24)

## 0.2.1 (2022-07-20)

## 0.2.0 (2022-07-20)
