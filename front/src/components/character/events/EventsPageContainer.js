import {connect} from "react-redux";
import EventsPage from "./EventsPage";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.params.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EventsPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EventsPage);

export default EventsPageContainer;
