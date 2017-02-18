import {connect} from "react-redux";
import {EntityDetails, ActivityDetails} from "./EntityDetails";
import {getSelectedDetails, fromEntitiesState} from "../../../modules/entities";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    details: getSelectedDetails(fromEntitiesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

export const EntityDetailsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EntityDetails);


export const ActivityDetailsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActivityDetails);

