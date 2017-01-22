import React from "react";
import {ListGroup, ListGroupItem, Panel} from "react-bootstrap";

class InventoryList extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Panel header="Inventory">
        <ListGroup fill>
          <ListGroupItem>A sword (equipped)</ListGroupItem>
          <ListGroupItem>5 lumps of clay</ListGroupItem>
          <ListGroupItem>An axe</ListGroupItem>
          <ListGroupItem>an ushanka hat (equipped)</ListGroupItem>
          <ListGroupItem>a hammer (equipped)</ListGroupItem>
          <ListGroupItem>a pairt of trousers (equipped)</ListGroupItem>
          <ListGroupItem>a shirt (equipped)</ListGroupItem>
          <ListGroupItem>a crossbow</ListGroupItem>
          <ListGroupItem>20 oak branches</ListGroupItem>
        </ListGroup>
      </Panel>);
  }
}

export default InventoryList;
