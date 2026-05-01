# Plot

## Instanced Members
> 🗣️ **Notice**\
> Instanced methods should be indexed with `:` when called.

### SetAppeal
Sets a plot's appeal. Will be naturally overwritten by the game unless you lock the appeal with [LockAppeal](#LockAppeal).

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| appeal | `integer` | Appeal to set the plot to. |

### LockAppeal
Locks or unlocks the appeal from being set. This will not prevent direct memory manipulation.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| toLock | `boolean` | `true` to lock the appeal, `false` to unlock it. |

# PlayerCities

## Instanced Members
> 🗣️ **Notice**\
> Instanced methods should be indexed with `:` when called.

### AddGreatWork
Finds a city to move a great work into.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| greatWorkListIndex | `integer` | This is **not** the `Index` column from the `GreatWorks` table. This is an integer assigned to great works that get created in-game by [CultureManager.FindOrAddGreatWork](/Wild-W/CivilizationVI_CommunityExtension/wiki/Singletons-&-Namespaces#FindOrAddGreatWork). |

# PlayerInfluence

## Instanced Members
> 🗣️ **Notice**\
> Instanced methods should be indexed with `:` when called.

### SetTokensToGive
Sets the number of free envoys.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| amount | `integer` | Number of envoys. |

### SetPoints
Sets the influence points.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| amount | `number` | Number of influence points. Overflow carries over. Total influence points are clamped to a lower bound of 0. |

### AdjustPoints
Adjusts the influence points.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| amount | `number` | Number to adjust influence points by. Overflow carries over. Total influence points are clamped to a lower bound of 0. |

# GameDiplomacy

## Instanced Members
> 🗣️ **Notice**\
> Instanced methods should be indexed with `:` when called.

### ChangeGrievanceScore
Changes the number of grievances between players. Does not immediately update UI.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| player1Id | `integer` | ID of the receiving player. |
| player2Id | `integer` | ID of the inflicting player. |
| amount | `integer` | Total score change, can be negative. |

# PlayerGovernors

## Instanced Members
> 🗣️ **Notice**\
> Instanced methods should be indexed with `:` when called.

### PromoteGovernor
Spends a governor title and assigns a promotion to a player's governor. Governor titles spent can be higher than the number earned, so you should balance each call of `PromoteGovernor` with `ChangeGovernorPoints(1)` or manually adjust the counters with memory manipulation.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| governorIndex | `integer` | `Index` column from the `Governors` table. |
| governorPromotionIndex | `integer` | `Index` column from the `GovernorPromotions` table. If the promotion doesn't exist for the given governor it won't be granted (needs more testing). If the promotion exists but is not accessible yet on the promotion tree, the promotion will be granted. |

#### Returns
| Return | Type | Description |
| - | - | - |
| success | `boolean` | `true` if valid `governorIndex` and `governorPromotionIndex` arguments were passed. `false` otherwise. |

### NeutralizeGovernor
Neutralizes a governor.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| governorIndex | `integer` | `Index` column from the `Governors` table. |
| neutralizedTurns | `integer` | Number of turns to neutralize. |

### ChangeNeutralizedTurns
Changes number of turns left until no longer neutralized.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| governorIndex | `integer` | `Index` column from the `Governors` table. |
| neutralizedTurns | `integer` | Number of turns to add to neutralized period. Can be negative. |

### GetNeutralizedIndefinitely
Unknown. Estimated use: Gets the number of `EFFECT_ADJUST_NEUTRALIZE_INDEFINITELY` modifiers attached.

#### Returns
| Return | Type | Description |
| - | - | - |
| count | `integer` | Total count of `EFFECT_ADJUST_NEUTRALIZE_INDEFINITELY`. |

### ChangeNeutralizedIndefinitely
Unknown. Estimated use: Changes number of `EFFECT_ADJUST_NEUTRALIZE_INDEFINITELY` modifiers attached. Can be used to prevent a player from using any governors.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| amount | `integer` | A value of `1` adds. A value of `-1` removes. |

### UnassignGovernor
Unassigns a governor from a city.

#### Parameters
| Parameter | Type | Description |
| - | - | - |
| governorIndex | `integer` | `Index` column from the `Governors` table. |
| unknown1 | `boolean` | Usually `false`. |
| unknown2 | `boolean` | Usually `true`. |