// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract SuperTrunfoCard is ERC721URIStorage, Ownable {
    uint256 private _nextTokenId;

    event CardMinted(address indexed to, uint256 indexed tokenId, string tokenUri);

    constructor(address initialOwner) ERC721("Super Trunfo Card", "STC") Ownable(initialOwner) {}

    function safeMint(address to, string memory tokenUri) external onlyOwner returns (uint256) {
        uint256 tokenId = ++_nextTokenId;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenUri);

        emit CardMinted(to, tokenId, tokenUri);

        return tokenId;
    }
}

