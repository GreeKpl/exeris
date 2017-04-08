import {connect} from "react-redux";
import Appearance from "./Appearance";
import {getMyCharacterInfoFromMyCharacterState} from "../../../modules/myCharacter";

const mapStateToProps = (state, ownProps) => {
  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    shortDescription: myCharacterInfo.get("shortDescription", ""),
    longDescription: myCharacterInfo.get("longDescription", ""),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const AppearanceContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Appearance);

export default AppearanceContainer;
