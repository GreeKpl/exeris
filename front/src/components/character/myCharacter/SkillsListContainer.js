import {connect} from "react-redux";
import SkillsList from "./SkillsList";
import {getMyCharacterInfoFromMyCharacterState} from "../../../modules/myCharacter";
import * as Immutable from "immutable";

const mapStateToProps = (state, ownProps) => {

  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    mainSkills: myCharacterInfo.get("skills", Immutable.List()),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const SkillsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(SkillsList);

export default SkillsListContainer;
