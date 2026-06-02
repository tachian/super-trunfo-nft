import { expect } from "chai";
import { network } from "hardhat";

describe("SuperTrunfoCard", () => {
  it("mints a card NFT with metadata URI", async () => {
    const { ethers } = await network.getOrCreate();
    const [owner, player] = await ethers.getSigners();
    const contractFactory = await ethers.getContractFactory("SuperTrunfoCard");
    const contract = await contractFactory.deploy(owner.address);

    await contract.safeMint(player.address, "ipfs://card-metadata");

    expect(await contract.ownerOf(1)).to.equal(player.address);
    expect(await contract.tokenURI(1)).to.equal("ipfs://card-metadata");
  });
});
