// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract Payment {
  struct User{
    uint id;
    string name;
  }
  struct Account{
    uint partner_id;
    uint balance;
  }
  mapping(uint => uint) id_index_map;
  mapping(uint => Account[]) accounts;
  User[] users;
  uint[] user_ids;

  event UserRegistered(uint id, string name);
  event AccountCreated(uint id, uint partner_id, uint balance);
  event TransactionStatus(bool success,uint id1, uint id2, uint amount,uint[] path);
  event AccountClosed(uint id1, uint id2);

  function doesUserExist(uint _id) public view returns(bool){
    for(uint i = 0; i < user_ids.length; i++){
      if(user_ids[i] == _id){
        return true;
      }
    }
    return false;
  }
  function registerUser(uint _id, string memory _name) public {
    require(!doesUserExist(_id), "User already registered");
    users.push(User(_id, _name));
    user_ids.push(_id);
    id_index_map[_id] = users.length - 1;
    emit UserRegistered(_id, _name);
  } 

  function createAcc(uint _id1, uint _id2, uint _balance) public {
    require(doesUserExist(_id1), "User1 not registered");
    require(doesUserExist(_id2), "User2 not registered");
    uint index1 = id_index_map[_id1];
    uint index2 = id_index_map[_id2];
    accounts[index1].push(Account(index2, _balance));
    accounts[index2].push(Account(index1, _balance));
    emit AccountCreated(_id1, _id2, _balance);
  }

  function getShortestPath(uint start,uint end) public view returns(uint[] memory){
    // use bfs to find the shortest path
    bool[] memory visited = new bool[](user_ids.length);
    uint[] memory parent = new uint[](user_ids.length);
    uint[] memory distance = new uint[](user_ids.length);

    for(uint i = 0; i < user_ids.length; i++){
      visited[i] = false;
      parent[i] = type(uint).max;
      distance[i] = type(uint).max;
    }

    uint[] memory queue = new uint[](user_ids.length);
    uint front = 0;
    uint rear = 0;
    queue[rear++] = start;

    visited[start] = true;
    distance[start] = 0;
    parent[start] = start;

    while(front < rear){
      uint curr = queue[front++];
      for(uint i = 0; i < accounts[curr].length; i++){
        uint next = accounts[curr][i].partner_id;
        if(!visited[next]){
          visited[next] = true;
          distance[next] = distance[curr] + 1;
          parent[next] = curr;
          queue[rear++] = next;
          if(next == end){
            uint[] memory path = new uint[](distance[end] + 1);
            curr = end;
            uint index = distance[end];
            while(curr != start){
              path[index--] = curr;
              curr = parent[curr];
            }
            path[index] = start;
            return path;
          }
        }
      }
    }
    return new uint[](0);
  }

  function canBeSent(uint[] memory path, uint _amount) public view returns(bool){
    for(uint i=0;i<(path.length-1);i++){
      uint curr = path[i];
      uint next = path[i+1];
      for(uint j=0;j<accounts[curr].length;j++){
        if(accounts[curr][j].partner_id == next){
          if(accounts[curr][j].balance < _amount){
            return false;
          }
          break;
        }
      }
    }
    return true;
  }

  function sendAlongPath(uint[] memory path, uint _amount) public {
    for(uint i=0;i<(path.length-1);i++){
      uint curr = path[i];
      uint next = path[i+1];
      for(uint j=0;j<accounts[curr].length;j++){
        if(accounts[curr][j].partner_id == next){
          accounts[curr][j].balance -= _amount;
          break;
        }
      }
      for(uint j=0;j<accounts[next].length;j++){
        if(accounts[next][j].partner_id == curr){
          accounts[next][j].balance += _amount;
          break;
        }
      }
    }
  }



  function sendAmount(uint _id1, uint _id2, uint _amount) public {
    require(doesUserExist(_id1), "User1 not registered");
    require(doesUserExist(_id2), "User2 not registered");
    
    uint index1 = id_index_map[_id1];
    uint index2 = id_index_map[_id2];
    uint[] memory path = getShortestPath(index1, index2);
    if(path.length == 0){
      emit TransactionStatus(false,_id1, _id2, _amount, path);
      return;
    }
    if(canBeSent(path, _amount)){
      sendAlongPath(path, _amount);
      emit TransactionStatus(true,_id1, _id2, _amount, path);
      return;
    }
    emit TransactionStatus(false,_id1, _id2, _amount, path);
    return;
  }

  function closeAccount(uint _id1, uint _id2) public {
    require(doesUserExist(_id1), "User1 not registered");
    require(doesUserExist(_id2), "User2 not registered");
    uint index1 = id_index_map[_id1];
    uint index2 = id_index_map[_id2];
    bool found = false;
    for(uint i = 0; i < accounts[index1].length; i++){
      if(accounts[index1][i].partner_id == index2){
        found = true;
        accounts[index1][i] = accounts[index1][accounts[index1].length - 1];
        accounts[index1].pop();
        break;
      }
    }
    for(uint i = 0; i < accounts[index2].length; i++){
      if(accounts[index2][i].partner_id == index1){
        accounts[index2][i] = accounts[index2][accounts[index2].length - 1];
        accounts[index2].pop();
        break;
      }
    }
    require(found, "Account not found");
    emit AccountClosed(_id1, _id2);
  }
}
