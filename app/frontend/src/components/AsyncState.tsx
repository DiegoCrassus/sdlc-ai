import styles from "./AsyncState.module.css";

interface AsyncStateProps {
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyMessage?: string;
  children: React.ReactNode;
}

export function AsyncState({
  loading,
  error,
  empty,
  emptyMessage = "No data yet.",
  children,
}: AsyncStateProps) {
  if (loading) {
    return <div className={styles.centered}>Loading…</div>;
  }

  if (error) {
    return (
      <div className={styles.error} role="alert">
        {error}
      </div>
    );
  }

  if (empty) {
    return <div className={styles.centered}>{emptyMessage}</div>;
  }

  return <>{children}</>;
}
