import {connect} from "react-redux";
import SpeechPanel from "./SpeechPanel";
import {
  updateText,
  getText,
  getSpeechTargetId,
  getSpeechType,
  fromSpeechState,
  speakText
} from "../../../modules/speech";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    text: getText(fromSpeechState(state, ownProps.characterId)),
    speechTarget: getSpeechTargetId(fromSpeechState(state, ownProps.characterId)),
    speechType: getSpeechType(fromSpeechState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onTextChange: (newText) => dispatch(updateText(ownProps.characterId, newText)),
    onSubmit: event => {
      event.preventDefault();
      dispatch(speakText(ownProps.characterId));
    },
  }
};

const SpeechPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(SpeechPanel);

export default SpeechPanelContainer;
