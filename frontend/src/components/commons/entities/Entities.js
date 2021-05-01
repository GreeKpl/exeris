import React from "react";
import {ListGroup, ListGroupItem, Button} from "react-bootstrap";
import * as Immutable from "immutable";
import "./style.scss";

class EntityInfo extends React.Component {
  constructor(props) {
    super(props);

    this.handleExpand = this.handleExpand.bind(this);
    this.handleCollapse = this.handleCollapse.bind(this);
    this.handleSelect = this.handleSelect.bind(this);
    this.handleDeselect = this.handleDeselect.bind(this);
  }

  render() {
    return <li className={"list-group-item EntitiesList-EntityInfo" + (this.props.isSelected ? " active" : "")}
               onClick={this.props.isSelected ? this.handleDeselect : this.handleSelect}>
      {this.props.entityInfo.get("rawName")}
      {this.props.entityInfo.get("expandable") && (!this.props.isExpanded ?
          <Button onClick={this.handleExpand}>\/</Button> :
          <Button onClick={this.handleCollapse}>/\</Button>
      )}
    </li>;
  }

  handleExpand(event) {
    event.preventDefault();
    event.stopPropagation();
    this.props.onExpand(this.props.entityInfo.get("id"));
  }

  handleCollapse(event) {
    event.preventDefault();
    event.stopPropagation();
    this.props.onCollapse(this.props.entityInfo.get("id"));
  }

  handleSelect(event) {
    event.preventDefault();
    this.props.onSelect(this.props.entityInfo.get("id"));
  }

  handleDeselect(event) {
    event.preventDefault();
    this.props.onDeselect(this.props.entityInfo.get("id"));
  }
}

class ActivityInfo extends EntityInfo {
  render() {
    const entityInfo = this.props.entityInfo;

    return <li className={"list-group-item EntitiesList-ActivityList" + (this.props.isSelected ? " active" : "")}
               onClick={this.props.isSelected ? this.handleDeselect : this.handleSelect}>
      {entityInfo.get("name")} {entityInfo.get("ticksNeeded") - entityInfo.get("ticksLeft")}{" "}
      / {entityInfo.get("ticksNeeded")}
    </li>;
  }
}

const Entities = ({entities, onExpand, onCollapse, onSelect, onDeselect, info, children, expanded, selectedEntities}) =>
  <ListGroup componentClass="ul" className="EntitiesList-EntityList">
    {entities.map(entityId => {
      const entityInfo = info.get(entityId);
      const isExpanded = expanded.has(entityId);
      const isSelected = selectedEntities.has(entityId);
      const childrenIds = children.get(entityId, Immutable.List());
      return [
        <EntityInfo key={entityId}
                    entityInfo={entityInfo}
                    onExpand={onExpand}
                    onCollapse={onCollapse}
                    onSelect={onSelect}
                    onDeselect={onDeselect}
                    isExpanded={isExpanded}
                    isSelected={isSelected}
        />].concat(
        entityInfo.get("activities").map(
          activityId => {
            const activityInfo = info.get(activityId);
            const isActivitySelected = selectedEntities.has(activityId);
            return <ActivityInfo key={"activity-" + activityId}
                                 entityInfo={activityInfo}
                                 onSelect={onSelect}
                                 onDeselect={onDeselect}
                                 isSelected={isActivitySelected}
            />;
          }
        )).concat(
        (isExpanded && childrenIds.size > 0) ?
          <ListGroupItem key={entityId + "-children"} className="EntitiesList-EntityChildren">
            <Entities entities={childrenIds}
                      onExpand={onExpand}
                      onCollapse={onCollapse}
                      onSelect={onSelect}
                      onDeselect={onDeselect}
                      info={info}
                      children={children}
                      expanded={expanded}
                      selectedEntities={selectedEntities}
            />
          </ListGroupItem> : []);
    })}
  </ListGroup>;

export default Entities;
