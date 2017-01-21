import React from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";

class ActionsList extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <ListGroup>
        <ListGroupItem href="#">Forging a sword</ListGroupItem>
        <ListGroupItem href="#">Building a hut</ListGroupItem>
        <ListGroupItem href="#">Building a field</ListGroupItem>
      </ListGroup>);
  }
}

export default ActionsList;
