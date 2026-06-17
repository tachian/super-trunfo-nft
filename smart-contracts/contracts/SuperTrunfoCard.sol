// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract SuperTrunfoCard is ERC721URIStorage, Ownable {
    uint256 private _nextTokenId;
    mapping(address account => bool enabled) private _authorizedMinters;

    event CardMinted(address indexed to, uint256 indexed tokenId, string tokenUri);
    event MinterUpdated(address indexed minter, bool enabled);

    error EmptyTokenUri();
    error UnauthorizedMinter(address account);

    constructor(address initialOwner) ERC721("Super Trunfo Card", "STC") Ownable(initialOwner) {}

    function safeMint(address to, string calldata tokenUri) external onlyAuthorizedMinter returns (uint256) {
        if (bytes(tokenUri).length == 0) {
            revert EmptyTokenUri();
        }

        uint256 tokenId = ++_nextTokenId;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenUri);

        emit CardMinted(to, tokenId, tokenUri);

        return tokenId;
    }

    function setMinter(address minter, bool enabled) external onlyOwner {
        _authorizedMinters[minter] = enabled;

        emit MinterUpdated(minter, enabled);
    }

    function isMinter(address account) external view returns (bool) {
        return _authorizedMinters[account];
    }

    function nextTokenId() external view returns (uint256) {
        return _nextTokenId + 1;
    }

    modifier onlyAuthorizedMinter() {
        address sender = _msgSender();

        if (sender != owner() && !_authorizedMinters[sender]) {
            revert UnauthorizedMinter(sender);
        }

        _;
    }
}
