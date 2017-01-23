import {connect} from "react-redux";
import CharacterTopPanel from "./CharacterTopPanel";
import {
  getDetailsData,
  fromTopPanelState,
} from "../../../modules/topPanel";


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    ...getDetailsData(fromTopPanelState(state, ownProps.characterId)).toObject(),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {}
};

const CharacterTopPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterTopPanel);

export default CharacterTopPanelContainer;
