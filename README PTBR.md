# Pokémon Legends: Arceus Recomp

![Preview](https://scontent.fjpa9-1.fna.fbcdn.net/v/t39.30808-6/871316188_4460131744202035_97881541406491077_n.jpg?stp=dst-jpg_tt6&cstp=mx1379x763&ctp=s1379x763&_nc_cat=101&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=aa7b47&_nc_ohc=cgH8xolutxAQ7kNvwE2jIyg&_nc_oc=AdpoS4OXukk4WXacp6zyvjHjzRIv8aHnPgsQkTHTgp2pUNiJw2mvAYvZfo6m1bxy0kw&_nc_zt=23&_nc_ht=scontent.fjpa9-1.fna&_nc_gid=otLAaRJZYd-ne225nuhEJg&_nc_ss=7b2a8&oh=00_AQQqKkMQq9dFRHhEZbORSUXcO14k8J_249NWBGK-stIR2g&oe=6AEE1D46)

![Preview](https://scontent.fjpa9-1.fna.fbcdn.net/v/t39.30808-6/870101848_4460518197496723_4891506017283762638_n.jpg?stp=dst-jpg_tt6&cstp=mx1919x1079&ctp=s1919x1079&_nc_cat=107&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=aa7b47&_nc_ohc=UawumFO82MQQ7kNvwHoRYRF&_nc_oc=Ado6EmCojxwW3dtQad0W9AQxlw0iTqBqjT1Zt18dOWAuAxnyxWMPrlu2mRTGHDSrLjw&_nc_zt=23&_nc_ht=scontent.fjpa9-1.fna&_nc_gid=Lj96yLSsWx5WYUtQ1LOC-Q&_nc_ss=7b2a8&oh=00_AQSO9mE7s2WGh4fOw2o6YILL139OWVI1fLyRyxLakdawqQ&oe=6AEE21BA)


Um projeto amador independente focado na recompilação de **Pokémon Legends: Arceus**.

Este projeto é uma experiência de aprendizado pessoal, desenvolvida com o conhecimento, tempo e recursos disponíveis. Estou fazendo o meu melhor para que funcione, aprimorá-lo e compartilhar meu progresso com a comunidade.

Não sou um desenvolvedor profissional e este não é um produto oficial, finalizado ou comercial. Bugs, limitações, problemas de compatibilidade e recursos incompletos são esperados.

## Apoie o Projeto

Se você gosta deste projeto e gostaria de me ajudar a dedicar mais tempo ao desenvolvimento, testes, solução de problemas e melhorias futuras, você pode me apoiar por meio de uma das opções abaixo.

- **Patreon:** Adicione o link da sua página do Patreon aqui.

- **Pix:** `53578c64-d11f-43c5-96b9-3b5529741664`

Toda contribuição é voluntária e apreciada. Obrigado por apoiar este projeto amador!

## Créditos e Isenção de Responsabilidade

Este é um projeto independente e não oficial feito por fãs. Não é afiliado, endossado ou patrocinado pela Nintendo ou Game Freak.

Projetos da comunidade como [LASRecomp](https://github.com/peiikai/LASRecomp) e [PokeZ-ARecomp](https://github.com/Hexveil404/PokeZ-ARecomp) serviram como referência para aprendizado e pesquisa. Os créditos por suas respectivas ferramentas e trabalhos pertencem aos seus autores originais.

Não distribua arquivos de jogos protegidos por direitos autorais, ROMs, recursos extraídos, código proprietário, chaves de criptografia ou outros materiais pertencentes à Nintendo ou Game Freak por meio deste repositório.


## Configurando os Arquivos do Jogo

Para recompilar e executar este projeto, você precisa fornecer os arquivos extraídos da sua própria cópia legal de **Pokémon Legends: Arceus**.

**Os arquivos originais do jogo não estão incluídos nem são distribuídos neste projeto.**

### 1. Extraia os arquivos do jogo

Você precisará extrair o conteúdo de ExeFS e RomFS da sua própria cópia do jogo.

### 2. Coloque os arquivos nas pastas corretas

Dentro do diretório principal do projeto, localize a pasta `extracted`.

Coloque os arquivos extraídos na seguinte estrutura:

```text
Pokemon Arceus Recompzada/
└── extracted/
    ├── exefs/
    │   ├── main
    │   ├── sdk
    │   ├── subsdk0
    │   ├── subsdk1
    │   └── outros arquivos ExeFS necessários
    │
    └── romfs/
        ├── bin/
        ├── system_resource/
        └── outros arquivos extraídos do jogo
```

**Importante:** Coloque o conteúdo das pastas ExeFS e RomFS dentro de suas respectivas pastas. Não coloque os arquivos compactados nem a pasta principal que contém ambas.

### 3. Recompile o jogo

Depois de configurar os arquivos:

1. Execute `recompilar_arceus.bat` ou `lasrecomp.exe`.
2. Aguarde a conclusão do processo de geração de código e compilação.
3. Quando a compilação terminar, execute `executar_arceus.bat` ou abra `lasrecomp.exe`.

A primeira compilação pode levar algum tempo, dependendo do hardware do seu computador.

### Aviso importante

Cada usuário deve fornecer os arquivos extraídos de sua própria cópia do jogo. Não compartilhe nem distribua arquivos originais pertencentes à Nintendo, Game Freak ou The Pokémon Company.
