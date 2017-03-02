import {connect} from "react-redux";
import CharacterPanel from "./CharacterPanel";
import {
  getDetailsData,
  fromTopPanelState, submitEditedName
} from "../../../modules/topPanel";


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    ...getDetailsData(fromTopPanelState(state, ownProps.characterId)).toObject(),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSubmitName: newName => {
      dispatch(submitEditedName(ownProps.characterId, newName));
    },
  }
};

const CharacterPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterPanel);

export default CharacterPanelContainer;
