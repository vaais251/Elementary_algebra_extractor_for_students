"use client";

import { useRef, useEffect } from "react";
import * as d3 from "d3";

/* ── Mock data mirroring Day 9 Python graph ── */
const nodes = [
  { id: "Basic Arithmetic" },
  { id: "Pre-Algebra" },
  { id: "Basic Algebra" },
  { id: "Factoring Polynomials" },
  { id: "Solving Quadratic Equations" },
];

const links = [
  { source: "Basic Arithmetic", target: "Pre-Algebra" },
  { source: "Pre-Algebra", target: "Basic Algebra" },
  { source: "Basic Algebra", target: "Factoring Polynomials" },
  { source: "Factoring Polynomials", target: "Solving Quadratic Equations" },
];

const CURRENT_TOPIC = "Solving Quadratic Equations";
const WIDTH = 600;
const HEIGHT = 400;

const ConceptGraph = () => {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    // CRITICAL: clear previous render to prevent duplicates in React strict mode
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Deep-copy data so D3 mutation doesn't break React re-renders
    const nodeData = nodes.map((n) => ({ ...n }));
    const linkData = links.map((l) => ({ ...l }));

    // ── Arrow marker definition ──
    svg
      .append("defs")
      .append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 22)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#64748b");

    // ── Force simulation ──
    const simulation = d3
      .forceSimulation(nodeData as d3.SimulationNodeDatum[])
      .force(
        "link",
        d3
          .forceLink(linkData)
          .id((d: any) => d.id)
          .distance(120)
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(WIDTH / 2, HEIGHT / 2));

    // ── Draw edges ──
    const link = svg
      .append("g")
      .selectAll("line")
      .data(linkData)
      .enter()
      .append("line")
      .attr("stroke", "#475569")
      .attr("stroke-width", 2)
      .attr("stroke-opacity", 0.7)
      .attr("marker-end", "url(#arrowhead)");

    // ── Draw nodes ──
    const node = svg
      .append("g")
      .selectAll("circle")
      .data(nodeData)
      .enter()
      .append("circle")
      .attr("r", 12)
      .attr("fill", (d: any) =>
        d.id === CURRENT_TOPIC ? "#ef4444" : "#6366f1"
      )
      .attr("stroke", (d: any) =>
        d.id === CURRENT_TOPIC ? "#fca5a5" : "#a5b4fc"
      )
      .attr("stroke-width", 2)
      .style("cursor", "grab");

    // ── Drag behavior ──
    node.call(
      d3
        .drag<SVGCircleElement, any>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );

    // ── Labels ──
    const label = svg
      .append("g")
      .selectAll("text")
      .data(nodeData)
      .enter()
      .append("text")
      .text((d: any) => d.id)
      .attr("font-size", "11px")
      .attr("font-family", "Inter, system-ui, sans-serif")
      .attr("fill", "#e2e8f0")
      .attr("text-anchor", "middle")
      .attr("dy", -18)
      .style("pointer-events", "none");

    // ── Tick handler ──
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);

      label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
    });

    // Cleanup on unmount
    return () => {
      simulation.stop();
    };
  }, []);

  return (
    <div className="w-full max-w-2xl mt-6 backdrop-blur-lg bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl shadow-cyan-500/5">
      <h2 className="text-sm font-semibold text-cyan-400 uppercase tracking-widest mb-4 flex items-center gap-2">
        <span className="inline-block w-2 h-2 rounded-full bg-cyan-400"></span>
        Concept Graph
      </h2>
      <p className="text-slate-500 text-xs mb-4">
        Drag nodes to explore. The{" "}
        <span className="text-red-400 font-medium">red node</span> is the
        current topic.
      </p>
      <svg
        ref={svgRef}
        width={WIDTH}
        height={HEIGHT}
        className="w-full rounded-xl bg-slate-950/50 border border-white/5"
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      />
    </div>
  );
};

export default ConceptGraph;
