> 🚧 **Under Construction**\
> This page is unfinished.

# Contributor's Guide

If you've found your way here, you're likely interested in contributing to the project. This guide is to help you get on track.

> 🛑 **STOP! Who goes there?**
>
> We do **NOT** condone, endorse, or promote the use of this knowledge for:
> * Developing, distributing, or using malware or other malicious tools.
> * Any form of cheating in multiplayer settings, manipulation of online game services, or disruption of other players' experiences.
> * Cracking or Circumventing Game Security Measures: Engaging in activities to crack games, bypass security measures, or circumvent copy protection systems is not only unethical, but also illegal. 

## Table of Contents
1. [Setting up Ghidra](#setting-up-ghidra)
2. [Further Resources](#further-resources)

## Setting up Ghidra
Ghidra is a binary analysis tool. Any should do but this one is free and fully featured. It's necessary to use a binary analysis tool to search the GameCore DLL and analyze the code.

---

### Step 1: Downloading and installing Ghidra
[Download Ghidra here](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_11.1.1_build) and follow the installation guide linked on that page if you're having difficulties.

### Step 2: Obtaining debug symbols
Debug symbols are supplementary materials that are generated during the linking phase of a project build. They are used to help software developers debug their program. They do this by labelling the addresses of global variables and functions so developers know where a problem occurred.

These symbols aren't meant to be shipped in public releases as their inclusion comprimises the entire program, making it significantly easier for reverse engineers to analyze the binary files.

There are several recorded instances of debug symbols for Gathering Storm's GameCore being leaked in public steam builds. First in 2020 and several more times in 2021 and 2023. Most times the symbols weren't in parity with the DLL they accompanied, so it was impossible to map them accordingly, but all it takes is once.

To obtain these symbols, open the Steam console by entering this command into your browser's search bar:
```
steam://open/console
```
Once it's open, run this command to download the correct manifest. It will only work if you own Gathering Storm.
```
download_depot 289070 947510 2550987199793754278
```
Here, `289070` means Civ VI, `947510` points to one of its depots, and `2550987199793754278` is the manifest for one of that depot's updates.

It may take time for the download to complete, and steam may not tell you when it's ready, so proceed.

Navigate to `steamapps\content\app_289070\depot_947510\DLC\Expansion2\Binaries\Win64`. If you don't see anything there your download hasn't finished yet.

### Step 3: Using Ghidra to analyze the binary

In Ghidra, create a new project and click `File > Import File`

![image](https://github.com/Wild-W/CivilizationVI_CommunityExtension/assets/39774593/f9a11afa-7e2c-4797-8464-35bd8bddcfd2)

Import `GameCore_XP2_FinalRelease.dll` from the downloaded depot. Once it's finished importing, open it and run the analyzer when prompted.

![image-1](https://github.com/Wild-W/CivilizationVI_CommunityExtension/assets/39774593/0cf93012-223c-4ffb-9eaf-c34863d70ff1)

This should take a while. There's a lot of code to analyze.

Once it's finished, click `File > Add to program` in the Code Browser window. (Not the main window)

![image-2](https://github.com/Wild-W/CivilizationVI_CommunityExtension/assets/39774593/66e57518-09a9-41ba-81d8-e108b7d90e16)

From the downloaded depot, find and add `GameCore_XP2_FinalRelease.map`. Make sure the format is set to "Microsoft Mapfile"

Once that process finishes, click `Window > Script Manager` to open the script manager.

![image-3](https://github.com/Wild-W/CivilizationVI_CommunityExtension/assets/39774593/e6febd79-ca01-4c5c-b188-c21013e66e00)

Search for "DemangleAll" and double click the script that comes up.

![image-4](https://github.com/Wild-W/CivilizationVI_CommunityExtension/assets/39774593/e1c471f2-6ec9-4695-8eb1-a017f2499256)

Congratulations! You now have a clean dissassembly of GameCore with all the symbols mapped!

When navigating the code, make sure to make use of the Data type manager, decompiler, functions, and defined strings windows. They will help you get to where you want to be.

If all you're interested in is learning how GameCore works and researching instanced offsets, you can stop here. To map these symbols to the latest version of GameCore, you'll need to learn how to use the Version Control Manager. Tutorial available soon.
