import pytest
from ferrox_py.pipelines.dag import DAG
from ferrox_py.pipelines.node import PipelineNode

@pytest.mark.asyncio
async def test_dag_execution():
    dag = DAG("test_dag")
    
    results = []
    
    async def task_a():
        results.append("A")
        return "A_res"
        
    async def task_b():
        results.append("B")
        return "B_res"
        
    async def task_c():
        results.append("C")
        return "C_res"
        
    node_a = PipelineNode(node_id="A", action=task_a)
    
    node_b = PipelineNode(node_id="B", action=task_b)
    node_b.depends_on("A")
    
    node_c = PipelineNode(node_id="C", action=task_c)
    node_c.depends_on("A", "B")
    
    dag.add_node(node_a)
    dag.add_node(node_b)
    dag.add_node(node_c)
    
    dag_results = await dag.execute()
    
    assert "A" in results
    assert "B" in results
    assert "C" in results
    
    assert dag_results["A"] == "A_res"
    assert dag_results["C"] == "C_res"
