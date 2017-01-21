import React from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";

class EntitiesList extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <ListGroup>
        <ListGroupItem>Your character</ListGroupItem>
        <ListGroupItem>An axe</ListGroupItem>
        <ListGroupItem>A house</ListGroupItem>
      </ListGroup>);
  }
}

export default EntitiesList;
