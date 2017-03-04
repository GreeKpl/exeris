import {connect} from "react-redux";
import EventsList from "./EventsList";
import {requestAllEvents, fromEventsState, getAllEvents} from "../../../modules/events";
import {parseHtmlToComponents} from "../../../util/parseDynamicName";


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
