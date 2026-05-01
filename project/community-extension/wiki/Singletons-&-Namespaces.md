# CityTradeManager

## Static Members
> 🗣️ **Notice**\
> Static methods should be indexed with `.`

### SetHasConstructedTradingPost
Creates or destroys a trading post.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| city | `City` | City to build or remove trading post from. |
| playerId | `integer` | ID of the player with the trading post. |
| toConstruct | `boolean` | Whether it has been constructed. |

# CultureManager

## Static Members
> 🗣️ **Notice**\
> Static methods should be indexed with `.`

### FindOrAddGreatWork
Finds or creates a new great work in-game given its database index.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| greatWorkIndex | `integer` | `Index` column from the `GreatWorks` database table. |

#### Returns
| Return | Type | Description |
| - | - | - |
| greatWorkListIndex | `integer` | Internal ID for great works that get created in-game. |

### SetGreatWorkPlayer
Gives a player ownership of a great work.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| greatWorkListIndex | `integer` | Internal ID for great works that get created in-game. |
| playerId | `integer` | ID of the player to give ownership to. |

#### Example
```lua
-- Create or find the great work
local greatWorkListIndex = CultureManager.FindOrAddGreatWork(GameInfo.GreatWorks.GREATWORK_MICHELANGELO_1.Index)
-- Give the great work to a player
CultureManager.SetGreatWorkPlayer(greatWorkListIndex, somePlayerId)
-- Add it to one of their cities if possible
Players[somePlayerId]:GetCities():AddGreatWork(greatWorkListIndex)
```

# EmergencyManager

## Static Members
> 🗣️ **Notice**\
> Static methods should be indexed with `.`

### ChangePlayerScore _#1_
Changes a player's current score in a COMPETITION emergency.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| playerId | `integer` | ID of the player to adjust the emergency score of. |
| emergencyHash | `integer` | `Hash` column from the `Emergencies_XP2` table. |
| amount | `integer` | Number to adjust the score by. |

### ChangePlayerScore _#2_
Changes a player's current score in an AID_REQUEST or HOSTILE_EMERGENCY emergency.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| playerId | `integer` | ID of the player to adjust the emergency score of. |
| otherPlayerId | `integer` | ID of the player that is being targeted by the emergency. |
| emergencyHash | `integer` | `Hash` column from the `Emergencies_XP2` table. |
| amount | `integer` | Number to adjust the score by. |

# EconomicManager

## Static Members
> 🗣️ **Notice**\
> Static methods should be indexed with `.`

### SetMonopolyTourismMultiplier _#1_
Sets the number to multiply global monopoly tourism by.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| amount | `number` | `0` will remove the tourism bonus altogether. `1` leaves it unchanged. |

### SetMonopolyTourismMultiplier _#2_
Sets the number to multiply player monopoly tourism by.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| playerId | `integer` | ID of the player. |
| amount | `number` | `0` will remove the tourism bonus altogether. `1` leaves it unchanged. |

### ChangeMonopolyTourismMultiplier _#1_
Adjusts the number to multiply global monopoly tourism by.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| amount | `number` | Amount to add/subtract from the modifier. |

### ChangeMonopolyTourismMultiplier _#2_
Adjusts the number to multiply player monopoly tourism by.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| playerId | `integer` | ID of the player. |
| amount | `number` | Amount to add/subtract from the modifier. |

### GetMonopolyTourismMultiplier _#1_
Gets the number that multiplies global monopoly tourism.

#### Returns
| Return | Type | Description |
| - | - | - |
| multiplier | `number` | `1` is the default. |

### GetMonopolyTourismMultiplier _#2_
Gets the number that multiplies a player's monopoly tourism.

#### Parameters
| Parameters | Type | Description |
| - | - | - |
| playerId | `integer` | ID of the player. |

#### Returns
| Return | Type | Description |
| - | - | - |
| multiplier | `number` | `1` is the default. |

### GetTourismFromMonopolies
Gets the total tourism a player gains per turn from monopolies.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| playerId | `integer` | ID of the player. |

#### Returns
| Return | Type | Description |
| - | - | - |
| tourism | `integer` | Tourism per turn. |

# GovernorManager

## Static Members
> 🗣️ **Notice**\
> Static methods should be indexed with `.`

### GetTurnsToEstablishDelay
Gets the number of turns that modifies the turns it takes a governor to establish.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| playerId | `integer` | ID of the player. |
| governorHash | `integer` | `Hash` column from the `Governors` table. |
| ui | `boolean` | If `true`, check for the delay visible from the Governors panel. If `false`, check for the delay that actually influences the time it takes to establish. |

#### Returns
| Return | Type | Description |
| - | - | - |
| turns | `integer` | Turn delay. |

### SetTurnsToEstablishDelay
Sets the number of turns that modifies the turns it takes a governor to establish.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| playerId | `integer` | ID of the player. |
| governorHash | `integer` | `Hash` column from the `Governors` table. |
| amount | `integer` | Number of turns. |
| updateUi | `boolean` | Whether to update the Governors' screen TurnsToEstablish counter. |

### ChangeTurnsToEstablishDelay
Changes the number of turns that modifies the turns it takes a governor to establish.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| playerId | `integer` | ID of the player. |
| governorHash | `integer` | `Hash` column from the `Governors` table. |
| amount | `integer` | Number of turns. |
| updateUi | `boolean` | Whether to update the Governors panel. |

# UnitManager
## Static Members
> 🗣️ **Notice**\
> Static methods should be indexed with `.`

### GetInstance
Gets a unit from its virtual address.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| address | `number` | Address of the unit. |

#### Returns
| Parameter | Type | Description |
| - | - | - |
| unit | `Unit\|nil` | A unit object. |

### ChangeOwner
Changes the owner of a unit.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| unit | `Unit` | Unit to transfer ownership of. |
| playerId | `integer` | ID of the player to receive the unit. |
| b1 | `boolean` | Unknown. Usually `false`. |
| b2 | `boolean` | Unknown. Usually `false`. |

#### Returns
| Return | Type | Description |
| - | - | - |
| newUnit | `Unit` | The unit after it gets transferred. |

# NationalParks
## Static Members
> 🗣️ **Notice**\
> Static methods should be indexed with `.`

### DesignatePark
Creates a 4 plot-sized national park.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| playerId | `integer` | Player that owns the park. |
| plotX | `integer` | X coordinate of the bottom plot. Must be a plot that is owned by the player. |
| plotY | `integer` | Y coordinate of the bottom plot. Must be a plot that is owned by the player. |

### FindPark
Gets the park at a certain coordinate.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| plotX | `integer` | X coordinate of a plot. |
| plotY | `integer` | Y coordinate of a plot. |

#### Returns
| Return | Type | Description |
| - | - | - |
| parkData | `userdata` | ParkData Struct. [Reference](https://docs.google.com/spreadsheets/d/1Yj7WHB0quLIVaXJFz7osZCkhX2WIxP7Y_CkBkRmQvkU/edit?usp=sharing) |

### RestoreVisualState
Gets the park at a certain coordinate.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| parkData | `userdata` | ParkData Struct. [Reference](https://docs.google.com/spreadsheets/d/1Yj7WHB0quLIVaXJFz7osZCkhX2WIxP7Y_CkBkRmQvkU/edit?usp=sharing) |