import {connect} from "react-redux";
import EventsList from "./EventsList";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EventsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EventsList);

export default EventsListContainer;
