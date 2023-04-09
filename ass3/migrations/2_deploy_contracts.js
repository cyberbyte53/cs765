var Payment = artifacts.require("../contracts/Payment.sol");

module.exports = function(deployer) {
  deployer.deploy(Payment);
};
