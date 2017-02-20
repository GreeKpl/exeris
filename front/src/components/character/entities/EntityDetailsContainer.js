import {connect} from "react-redux";
import {EntityDetails, ActivityDetails} from "./EntityDetails";
import {getSelectedDetails, fromEntitiesState, updateExpandedInput} from "../../../modules/entities";
import {performAddEntityToItemAction} from "../../../modules/entities-actionsAddon";

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
  (dispatch, ownProps) => {
    return {
      onSubmitForm: (activityId, reqGroup, addedItemId, amount) => {
        dispatch(performAddEntityToItemAction(ownProps.characterId,
          activityId, reqGroup, addedItemId, amount));
      },
      onExpandInput: inputName => {
        dispatch(updateExpandedInput(ownProps.characterId, inputName));
      },
      onCollapseInput: () => {
        dispatch(updateExpandedInput(ownProps.characterId, null));
      }
    }
  }
)(ActivityDetails);
