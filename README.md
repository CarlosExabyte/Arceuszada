# Pokémon Legends: Arceus Recomp

![Preview](https://scontent.fjpa9-1.fna.fbcdn.net/v/t39.30808-6/871316188_4460131744202035_97881541406491077_n.jpg?stp=dst-jpg_tt6&cstp=mx1379x763&ctp=s1379x763&_nc_cat=101&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=aa7b47&_nc_ohc=cgH8xolutxAQ7kNvwE2jIyg&_nc_oc=AdpoS4OXukk4WXacp6zyvjHjzRIv8aHnPgsQkTHTgp2pUNiJw2mvAYvZfo6m1bxy0kw&_nc_zt=23&_nc_ht=scontent.fjpa9-1.fna&_nc_gid=otLAaRJZYd-ne225nuhEJg&_nc_ss=7b2a8&oh=00_AQQqKkMQq9dFRHhEZbORSUXcO14k8J_249NWBGK-stIR2g&oe=6AEE1D46)

![Preview](https://scontent.fjpa9-1.fna.fbcdn.net/v/t39.30808-6/870101848_4460518197496723_4891506017283762638_n.jpg?stp=dst-jpg_tt6&cstp=mx1919x1079&ctp=s1919x1079&_nc_cat=107&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=aa7b47&_nc_ohc=UawumFO82MQQ7kNvwHoRYRF&_nc_oc=Ado6EmCojxwW3dtQad0W9AQxlw0iTqBqjT1Zt18dOWAuAxnyxWMPrlu2mRTGHDSrLjw&_nc_zt=23&_nc_ht=scontent.fjpa9-1.fna&_nc_gid=Lj96yLSsWx5WYUtQ1LOC-Q&_nc_ss=7b2a8&oh=00_AQSO9mE7s2WGh4fOw2o6YILL139OWVI1fLyRyxLakdawqQ&oe=6AEE21BA)

An independent amateur project focused on the recompilation of **Pokémon Legends: Arceus**.

This project is a personal learning experience, developed with the knowledge, time, and resources available to me. I'm doing my best to make it work, improve it, and share my progress with the community.

I'm not a professional developer, and this is not an official, finished, or commercial product. Bugs, limitations, compatibility issues, and incomplete features are to be expected.

## Support the Project

If you enjoy this project and would like to help me dedicate more time to development, testing, troubleshooting, and future improvements, you can support me through either option below.

- **Patreon:** (https://www.patreon.com/cw/CarlosExabyte)
- **Pix:** `53578c64-d11f-43c5-96b9-3b5529741664`

Every contribution is voluntary and appreciated. Thank you for supporting this amateur project!

## Credits and Disclaimer

This is an independent, unofficial fan project. It is not affiliated with, endorsed by, or sponsored by Nintendo or Game Freak.

Community projects such as [LASRecomp](https://github.com/peiikai/LASRecomp) and [PokeZ-ARecomp](https://github.com/Hexveil404/PokeZ-ARecomp) served as references for learning and research. Credit for their respective tools and work belongs to their original authors.

Do not distribute copyrighted game files, ROMs, extracted assets, proprietary code, encryption keys, or other materials belonging to Nintendo or Game Freak through this repository.

## Setting Up the Game Files

To recompile and run this project, you must provide the extracted files from your own legal copy of **Pokémon Legends: Arceus**.

**Original game files are not included or distributed with this project.**

### 1. Extract the Game Files

You will need the ExeFS and RomFS contents extracted from your own copy of the game.

### 2. Place the Files in the Correct Folders

Inside the main project directory, locate the `extracted` folder.

Place the extracted files in the following structure:

```text
Pokemon Arceus Recompzada/
└── extracted/
    ├── exefs/
    │   ├── main
    │   ├── sdk
    │   ├── subsdk0
    │   ├── subsdk1
    │   └── other required ExeFS files
    │
    └── romfs/
        ├── bin/
        ├── system_resource/
        └── other extracted game files
```

**Important:** Place the contents of ExeFS and RomFS inside their respective folders. Do not place the compressed archives or the parent folder containing both directories there.

### 3. Recompile the Game

After setting up the files:

1. Run `recompilar_arceus.bat` or `lasrecomp.exe`.
2. Wait for the code generation and compilation process to finish.
3. Once compilation is complete, run `executar_arceus.bat` or open `lasrecomp.exe`.

The first compilation may take some time, depending on your computer's hardware.

### Important Notice

Each user must provide files extracted from their own copy of the game. Do not share or distribute original game files belonging to Nintendo, Game Freak, or The Pokémon Company.
