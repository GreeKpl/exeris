import React from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";

class InventoryList extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <ListGroup striped={true}>
        <ListGroupItem>A sword (equipped)</ListGroupItem>
        <ListGroupItem>5 lumps of clay</ListGroupItem>
        <ListGroupItem>An axe</ListGroupItem>
        <ListGroupItem>an ushanka hat (equipped)</ListGroupItem>
        <ListGroupItem>a hammer (equipped)</ListGroupItem>
        <ListGroupItem>a pairt of trousers (equipped)</ListGroupItem>
        <ListGroupItem>a shirt (equipped)</ListGroupItem>
        <ListGroupItem>a crossbow</ListGroupItem>
        <ListGroupItem>20 oak branches</ListGroupItem>
      </ListGroup>);
  }
}

export default InventoryList;
