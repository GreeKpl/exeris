import {connect} from "react-redux";
import SkillsList from "./SkillsList";
import {getEntityId, fromMyCharacterState} from "../../../modules/myCharacter";
import {getEntityInfo, fromEntitiesState} from "../../../modules/entities";
import * as Immutable from "immutable";

const mapStateToProps = (state, ownProps) => {

  const characterEntityId = getEntityId(fromMyCharacterState(state, ownProps.characterId));
  const entityInfo = getEntityInfo(characterEntityId, fromEntitiesState(state, ownProps.characterId));
  return {
    characterId: ownProps.characterId,
    mainSkills: entityInfo.get("skills", Immutable.List()),
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
