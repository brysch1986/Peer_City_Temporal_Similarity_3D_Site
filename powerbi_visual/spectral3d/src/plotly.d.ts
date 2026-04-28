/**
 * Minimal type declarations for plotly.js-dist-min.
 * Covers only what this visual uses (scatter3d traces).
 * Avoids the @types/plotly.js peer-dependency conflict with the dist package.
 */
declare module "plotly.js-dist-min" {

    interface LineStyle {
        width?: number;
        color?: string;
    }

    interface MarkerStyle {
        size?: number;
        color?: string | string[];
        line?: LineStyle;
    }

    interface Scatter3dTrace {
        type: "scatter3d";
        x: (number | null)[];
        y: (number | null)[];
        z: (number | null)[];
        mode?: string;
        line?: LineStyle;
        marker?: MarkerStyle;
        text?: string | string[];
        textposition?: string;
        hovertext?: string | string[];
        hoverinfo?: string;
        showlegend?: boolean;
    }

    type Data = Scatter3dTrace | Record<string, unknown>;

    interface SceneAxisLayout {
        visible?: boolean;
    }

    interface Layout {
        autosize?: boolean;
        scene?: {
            xaxis?: SceneAxisLayout;
            yaxis?: SceneAxisLayout;
            zaxis?: SceneAxisLayout;
        };
        margin?: { l?: number; r?: number; t?: number; b?: number };
        paper_bgcolor?: string;
        title?: string | { text: string };
        [key: string]: unknown;
    }

    interface Config {
        responsive?: boolean;
        displayModeBar?: boolean;
    }

    function react(
        root: HTMLElement | string,
        data: Data[],
        layout?: Partial<Layout>,
        config?: Partial<Config>
    ): Promise<HTMLElement>;

    function purge(root: HTMLElement | string): void;
}
