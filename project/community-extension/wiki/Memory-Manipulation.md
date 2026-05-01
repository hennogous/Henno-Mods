# Memory Manipulation
One of the core features of this mod is the ability to directly fetch and manipulate program memory during runtime. What this means for you, the mod creator, is that you can change *any*<sup>[1](#footnote1)</sup> number or string that exists within the game, provided you know its virtual address.

Inspired by [LunaLua](https://github.com/WohlSoft/LunaLua)
> ⚠️ **Warning**\
> Directly manipulating memory may lead to unexpected behavior, including crashing the game.\
> Make sure you know what your code is doing before you ship it in a mod.

## Global Members

### Field Types
| Name | Value | Type | Alignment |
| - | - | - | - |
| FIELD_BYTE | 0 | `unsigned char` | 1 byte |
| FIELD_SHORT | 1 | `short` | 2 bytes |
| FIELD_UNSIGNED_SHORT | 2 | `unsigned short` | 2 bytes |
| FIELD_INT | 3 | `int` | 4 bytes |
| FIELD_UNSIGNED_INT | 4 | `unsigned int` | 4 bytes |
| FIELD_LONG_LONG | 5 | `long long` | 8 bytes |
| FIELD_UNSIGNED_LONG_LONG | 6 | `unsigned long long` | 8 bytes |
| FIELD_CHAR | 7 | `char` | 1 byte |
| FIELD_FLOAT | 8 | `float` | 4 bytes |
| FIELD_DOUBLE | 9 | `double` | 8 bytes |
| FIELD_C_STRING | 10 | `char*` | 8 bytes |
| FIELD_BOOL | 11 | `bool` | 1 byte |
| FIELD_POINTER | 12 | `unsigned long long` | 8 bytes |

### Mem
Manipulates and returns global GameCore memory. *Usually not that useful, for most purposes you'll want [ObjMem](#ObjMem)*.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| address | `integer` | Offset address to a piece of memory in GameCore. |
| fieldType | `FieldType` | The type of memory stored at the address. This information is used to interpret and modify the data correctly. |
| newValue | `number\|string\|boolean\|nil` | The new value to be stored in the address. Optional. |

#### Returns
| Return | Type | Description |
| - | - | - |
| value | `number\|string\|boolean\|nil` | The value at the address. `nil` if a third argument is passed. |

### ObjMem
Manipulates and returns instanced memory.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| object | `object` | A valid object with the `__instance` field. |
| address | `integer` | Offset address to a piece of memory in GameCore. |
| fieldType | `FieldType` | The type of memory stored at the address. This information is used to interpret and modify the data correctly. |
| newValue | `number\|string\|boolean\|nil` | The new value to be stored in the address. Optional. |

#### Returns
| Return | Type | Description |
| - | - | - |
| value | `number\|string\|boolean\|nil` | The value at the address. `nil` if a fourth argument is passed. |

#### Example
```lua
-- Get the appeal of a plot
local appeal = ObjMem(pPlot, 0x4a, FIELD_SHORT)
-- Set the appeal of a plot
ObjMem(pPlot, 0x4a, FIELD_SHORT, 900)
```

### RegisterCallEvent
> 🚧 **Under construction**\
> This feature is yet to function properly. Avoid using.

Registers an event callback at a function in GameCore memory. Captures four or less arguments.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| callback | `function` | A function with up to four arguments. |
| address | `integer` | Offset address to function in GameCore. |
| parameters | `FieldType[]` | An array of `FieldType`; denotes the number of parameters (up to four) and their types. |

#### Example
```lua
function OnPlayerUnitsDestroy(playerUnitsAddress, unitInstanceAddress)
    local unit = UnitManager.GetInstance(unitInstanceAddress)
    print("Unit destroyed at: x=" .. unit:GetX() .. ", y=" .. unit:GetY() .. "!")
end

RegisterCallEvent(OnPlayerUnitsDestroy, 0x34d4e0, { FIELD_POINTER, FIELD_POINTER })
```

## Known offsets

### Instanced

#### Plot
| Address | FieldType | Description |
| - | - | - |
| 0x4a | FIELD_SHORT | The appeal of the plot |

#### PlayerInfluence
| Address | FieldType | Description |
| - | - | - |
| 0xb8 | FIELD_UNSIGNED_INT | The total influence points, multiplied by 256 |

#### Player
| Address | FieldType | Description |
| - | - | - |
| 0xd8 | FIELD_INT | Unknown |

#### UnitExperience
| Address | FieldType | Description |
| - | - | - |
| 0xc | FIELD_INT | The amount of experience |
| 0x10 | FIELD_INT | Level of the unit |

#### Unit
| Address | FieldType | Description |
| - | - | - |
| 0x128 | FIELD_INT | The playerId of the unit's owner. Simply setting this is not enough to gift a unit |

---

<a name="footnote1">1</a>: Trying to overwrite executable memory will result in an error. Not because it isn't possible but because it's dangerous and highly suspicious.
