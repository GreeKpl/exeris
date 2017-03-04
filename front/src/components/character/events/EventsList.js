import React from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";


class EventsList extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.requestState();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.characterId !== this.props.characterId) {
      this.props.requestState();
    }
  }

  render() {
    let eventsList = [];
    const events = this.props.events;
    for (let i = events.size - 1; i >= 0; i--) {
      eventsList.push(
        <ListGroupItem key={events.get(i).get("id")}>
          {events.get(i).get("textComponent")}
        </ListGroupItem>
      );
    }

    return (
      <ListGroup>
        {eventsList}
      </ListGroup>);
  }
}

export default EventsList;
