import {connect} from "react-redux";
import {CharacterDialogs} from "./CharacterDialogs";
import {getDetailsType, fromDetailsState, getDetailsTarget} from "../../../modules/details";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    dialogType: getDetailsType(fromDetailsState(state, ownProps.characterId)),
    targetId: getDetailsTarget(fromDetailsState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const CharacterDialogsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterDialogs);

export default CharacterDialogsContainer;
