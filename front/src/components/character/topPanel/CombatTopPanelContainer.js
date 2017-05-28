import {connect} from "react-redux";
import TopPanel from "./CombatTopPanel";
import {
  fromDetailsState, getDetailsTarget
} from "../../../modules/details";
import {getEntityInfo, fromEntitiesState} from "../../../modules/entities";

const characterSpecificState = (characterId, combatState) => {
  const characterFighter = combatState.get("attackers")
    .concat(combatState.get("defenders"))
    .filter(fighter => fighter.get("id") === characterId).get(0, null);
  return {
    inCombat: characterFighter !== null,
    stance: characterFighter.get("stance", null),
    ...combatState.toJS(),
  };
};

const mapStateToProps = (state, ownProps) => {
  const combatId = getDetailsTarget(fromDetailsState(state, ownProps.characterId));
  const entityInfo = getEntityInfo(combatId, fromEntitiesState(state, ownProps.characterId));
  return {
    characterId: ownProps.characterId,
    ...characterSpecificState(ownProps.characterId, entityInfo),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {}
};

const CombatTopPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TopPanel);

export default CombatTopPanelContainer;
