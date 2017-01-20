import {connect} from "react-redux";
import SpeakPanel from "./SpeakPanel";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    speakTarget: 0,
    speakType: "aloud",
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EventsPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(SpeakPanel);

export default EventsPageContainer;
