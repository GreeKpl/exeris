import {connect} from "react-redux";
import {requestAllEvents, fromEventsState, getAllEvents} from "../../../modules/events";
import {parseHtmlToComponents} from "../../../util/parseDynamicName";
import React from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";


export class EventsList extends React.Component {
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


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    events: getAllEvents(fromEventsState(state, ownProps.characterId)).map(event => {
      const eventAsComponent = parseHtmlToComponents(ownProps.characterId, event.get("text"));
      return event.set("textComponent", eventAsComponent);
    }),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {requestState: () => dispatch(requestAllEvents(ownProps.characterId))}
};

const EventsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EventsList);

export default EventsListContainer;
