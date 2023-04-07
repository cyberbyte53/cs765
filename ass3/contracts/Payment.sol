// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract Payment {
  struct User{
    string user_name;
    JointAccount[] joint_accounts;
  }
  struct JointAccount{
    uint partner;
    uint my_contribution;
  }
  mapping(uint => User) public users;

  constructor() public {
    
  }
  event UserRegistered(uint user_id, string user_name);
  event AccountCreated(uint user_id1,uint user_id2,uint user_id1_contribution,uint user_id2_contribution);

  function doesUserExist(uint user_id) public view returns (bool) {
    return bytes(users[user_id].user_name).length > 0;
  }

  function registerUser(uint user_id, string memory user_name) public {
    // check if user already exists
    require(!doesUserExist(user_id), "User already exists");
    users[user_id] = User(user_name,new JointAccount[](0));
    emit UserRegistered(user_id, user_name);

  }
  function createAcc(uint user_id1,uint user_id2,uint amount) public {
    // check if user already exists
    require(doesUserExist(user_id1), "User1 does not exists");
    require(doesUserExist(user_id2), "User2 does not exists");
    users[user_id1].joint_accounts.push(JointAccount(user_id2,amount));
    users[user_id2].joint_accounts.push(JointAccount(user_id1,amount));
    emit AccountCreated(user_id1,user_id2,amount,amount);
  }
  function sendAmount(uint user_id1,uint user_id2,uint amount) public {
    // 1st find a path from user_id1 to user_id2
    // 2nd check all outgoing edges from intermediate nodes in the paths have enough balance
    
  }
  function closeAccount(uint user_id1,uint user_id2) public {}
  

}
