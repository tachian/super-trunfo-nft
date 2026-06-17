import { expect } from "chai";
import { network } from "hardhat";

async function deploySuperTrunfoCard() {
  const { ethers } = await network.getOrCreate();
  const [owner, minter, player, attacker] = await ethers.getSigners();
  const contractFactory = await ethers.getContractFactory("SuperTrunfoCard");
  const contract = await contractFactory.deploy(owner.address);

  return { attacker, contract, minter, owner, player };
}

describe("SuperTrunfoCard", () => {
  it("mints a card NFT with metadata URI by owner", async () => {
    const { contract, owner, player } = await deploySuperTrunfoCard();
    const metadataUri = "ipfs://card-metadata";

    await expect(contract.connect(owner).safeMint(player.address, metadataUri))
      .to.emit(contract, "CardMinted")
      .withArgs(player.address, 1n, metadataUri);

    expect(await contract.ownerOf(1)).to.equal(player.address);
    expect(await contract.tokenURI(1)).to.equal(metadataUri);
    expect(await contract.nextTokenId()).to.equal(2n);
  });

  it("allows owner to authorize and revoke minters", async () => {
    const { contract, minter, owner, player } = await deploySuperTrunfoCard();
    const metadataUri = "ipfs://authorized-card";

    await expect(contract.connect(owner).setMinter(minter.address, true))
      .to.emit(contract, "MinterUpdated")
      .withArgs(minter.address, true);
    expect(await contract.isMinter(minter.address)).to.equal(true);

    await expect(contract.connect(minter).safeMint(player.address, metadataUri))
      .to.emit(contract, "CardMinted")
      .withArgs(player.address, 1n, metadataUri);

    await expect(contract.connect(owner).setMinter(minter.address, false))
      .to.emit(contract, "MinterUpdated")
      .withArgs(minter.address, false);
    expect(await contract.isMinter(minter.address)).to.equal(false);

    await expect(
      contract.connect(minter).safeMint(player.address, "ipfs://revoked-card"),
    )
      .to.be.revertedWithCustomError(contract, "UnauthorizedMinter")
      .withArgs(minter.address);
  });

  it("rejects mint attempts from unauthorized accounts", async () => {
    const { attacker, contract, player } = await deploySuperTrunfoCard();

    await expect(
      contract
        .connect(attacker)
        .safeMint(player.address, "ipfs://blocked-card"),
    )
      .to.be.revertedWithCustomError(contract, "UnauthorizedMinter")
      .withArgs(attacker.address);
  });

  it("rejects empty metadata URI", async () => {
    const { contract, owner, player } = await deploySuperTrunfoCard();

    await expect(
      contract.connect(owner).safeMint(player.address, ""),
    ).to.be.revertedWithCustomError(contract, "EmptyTokenUri");
  });
});
