import {connect} from "react-redux";
import EventsList from "./EventsList";
import {requestAllEvents, fromEventsState, getAllEvents} from "../../../modules/events";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    events: getAllEvents(fromEventsState(state, ownProps.characterId)),
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
