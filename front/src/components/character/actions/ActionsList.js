import React from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";

class ActionsListItem extends React.Component {
  constructor(props) {
    super(props);

    this.handleClick = this.handleClick.bind(this);
  }

  render() {
    return <ListGroupItem onClick={this.handleClick}
                          disabled={!this.props.action.get("enabled")}>
      {this.props.action.get("name")}
    </ListGroupItem>;
  }

  handleClick() {
    this.props.onSelectAction(this.props.action.get("id"));
  }
}

class ActionsList extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.requestState();
  }

  render() {
    return (
      <ListGroup>
        {this.props.actionsList.map(action =>
          <ActionsListItem onSelectAction={this.props.onSelectAction}
                           action={action}
                           key={action.get("id")}/>)}

      </ListGroup>);
  }
}

export default ActionsList;
