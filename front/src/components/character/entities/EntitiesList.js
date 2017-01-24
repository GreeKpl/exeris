import React from "react";
import {ListGroup, ListGroupItem, Button} from "react-bootstrap";
import * as Immutable from "immutable";


class EntityInfo extends React.Component {
  constructor(props) {
    super(props);

    this.handleExpand = this.handleExpand.bind(this);
    this.handleCollapse = this.handleCollapse.bind(this);
  }

  render() {
    return <ListGroupItem>
      {this.props.entityInfo.get("id").substring(0, 4)} {this.props.entityInfo.get("name")}
      {this.props.entityInfo.get("expandable") && (!this.props.isExpanded ?
          <Button onClick={this.handleExpand}>\/</Button> :
          <Button onClick={this.handleCollapse}>/\</Button>
      )}
    </ListGroupItem>;
  }

  handleExpand(event) {
    event.preventDefault();
    this.props.onExpand(this.props.entityInfo.get("id"));
  }

  handleCollapse(event) {
    event.preventDefault();
    this.props.onCollapse(this.props.entityInfo.get("id"));
  }
}

const Entities = ({entities, onExpand, onCollapse, info, children, expanded}) =>
  <ListGroup>
    {entities.map(entityId => {
      const entityInfo = info.get(entityId);
      const isExpanded = expanded.has(entityId);
      const childrenIds = children.get(entityId, Immutable.List());
      return [
        <EntityInfo key={entityId}
                    entityInfo={entityInfo}
                    onExpand={onExpand}
                    onCollapse={onCollapse}
                    isExpanded={isExpanded}
        />,
        (isExpanded && childrenIds.size > 0) ?
          <ListGroupItem key={entityId + "-children"}>
            <Entities entities={childrenIds}
                      onExpand={onExpand}
                      onCollapse={onCollapse}
                      info={info}
                      children={children}
                      expanded={expanded}
            />
          </ListGroupItem> : null
      ];
    })}
  </ListGroup>;


class EntitiesList extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.requestState();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.characterId !== this.props.characterId) {
      this.props.requestState();
    }
  }

  render() {
    return <Entities entities={this.props.rootEntities} {...this.props}/>;
  }
}

export default EntitiesList;
