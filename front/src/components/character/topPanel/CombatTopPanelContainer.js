import {connect} from "react-redux";
import TopPanel from "./CombatTopPanel";
import {
  getDetailsData,
  fromTopPanelState,
} from "../../../modules/topPanel";

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
  return {
    characterId: ownProps.characterId,
    ...characterSpecificState(ownProps.characterId, getDetailsData(fromTopPanelState(state, ownProps.characterId))),
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
