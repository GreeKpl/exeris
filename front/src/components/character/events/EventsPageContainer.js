import {connect} from "react-redux";
import EventsPage from "./EventsPage";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.params.characterId,
    isSmall: state.get("browser").atMost.small,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EventsPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EventsPage);

export default EventsPageContainer;
